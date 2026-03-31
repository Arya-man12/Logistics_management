from app.exceptions.custom_exceptions import ValidationException
from app.utils.constants import HUB_STATUSES, PAYMENT_STATUSES, SHIPMENT_STATUSES, USER_ROLES


def validate_role(role: str) -> str:
    if role not in USER_ROLES:
        raise ValidationException(f"Unsupported role: {role}")
    return role


def validate_shipment_status(status: str) -> str:
    if status not in SHIPMENT_STATUSES:
        raise ValidationException(f"Unsupported shipment status: {status}")
    return status


def validate_hub_status(status: str) -> str:
    if status not in HUB_STATUSES:
        raise ValidationException(f"Unsupported hub status: {status}")
    return status


def validate_payment_status(status: str) -> str:
    if status not in PAYMENT_STATUSES:
        raise ValidationException(f"Unsupported payment status: {status}")
    return status

