import pytest
from unittest.mock import Mock, patch

from app.exceptions.custom_exceptions import AuthorizationException, ShipmentNotFoundException
from app.schemas.shipment_schema import ShipmentCreate
from app.services.shipment_service import ShipmentService


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def tracking_service():
    return Mock()


@patch("app.services.shipment_service.get_redis", return_value=None)
@patch("app.services.shipment_service.generate_tracking_number", return_value="TRKTEST12345")
def test_create_shipment_generates_tracking_number(
    patched_tracking_number,
    patched_get_redis,
    repository,
    tracking_service,
):
    payload = ShipmentCreate(
        source_address="Origin addr",
        destination_address="Destination addr",
        package_description="Test package",
        weight_kg=2.3,
    )

    repository.create_shipment.return_value = {
        "id": "shipment-1",
        "tracking_number": "TRKTEST12345",
        "status": "created",
        "customer_id": "cust-1",
        "source_address": "Origin addr",
        "destination_address": "Destination addr",
        "package_description": "Test package",
        "weight_kg": 2.3,
        "dimensions": None,
        "service_type": "standard",
        "payment_status": "pending",
        "assigned_agent_id": None,
        "created_at": "2026-03-30T00:00:00Z",
        "updated_at": "2026-03-30T00:00:00Z",
    }

    service = ShipmentService(repository=repository, tracking_service=tracking_service)
    result = service.create_shipment(payload, customer_id="cust-1")

    assert result["tracking_number"] == "TRKTEST12345"
    repository.create_shipment.assert_called_once()
    tracking_service.create_tracking_update.assert_called_once()


@patch("app.services.shipment_service.get_redis", return_value=None)
def test_update_status_raises_when_agent_not_assigned(
    patched_get_redis,
    repository,
    tracking_service,
):
    repository.get_shipment_by_id.return_value = {
        "id": "shipment-1",
        "assigned_agent_id": "agent-1",
        "customer_id": "cust-1",
    }

    service = ShipmentService(repository=repository, tracking_service=tracking_service)

    with pytest.raises(AuthorizationException):
        service.update_status(
            "shipment-1",
            "in_transit",
            agent_id="agent-2",
            location="Hub A",
            note="update",
        )

