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
