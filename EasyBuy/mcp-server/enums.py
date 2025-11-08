from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class PaymentMethod(str, Enum):
    CASH_ON_DELIVERY = "CASH_ON_DELIVERY"
    EASYPAISA = "EASYPAISA"
    NAYAPAY = "NAYAPAY"
    STRIPE = "STRIPE"

    @classmethod
    def from_str(cls, value: str) -> "PaymentMethod":
        """
        Converts a flexible, user-provided string (e.g., 'cash on delivery', 'Cash On Delivery')
        into the corresponding PaymentMethod enum value.

        Raises:
            ValueError: If no valid match is found.
        """
        if not isinstance(value, str):
            raise ValueError(f"Expected a string for payment method, got {type(value)}")

        normalized = value.strip().replace(" ", "_").upper()

        # Allow exact matches to enum values
        for method in cls:
            if method.value == normalized:
                return method

        raise ValueError(f"Invalid payment method: {value}. Valid options are: {[m.value for m in cls]}")