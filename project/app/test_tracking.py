import pytest
from unittest.mock import Mock

from app.exceptions.custom_exceptions import TrackingNotFoundException
from app.schemas.tracking_schema import TrackingUpdate
from app.services.tracking_service import TrackingService


def test_update_tracking_raises_when_missing():
    repository = Mock()
    service = TrackingService(repository=repository)
    payload = TrackingUpdate(status="delivered")
    repository.update_tracking.return_value = None

    with pytest.raises(TrackingNotFoundException):
        service.update_tracking("missing", payload)


