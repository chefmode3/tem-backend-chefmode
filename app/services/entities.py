import os
import enum
from datetime import datetime
from typing import List, Tuple, Optional

from pydantic import BaseModel


class MembershipStates(str, enum.Enum):
    UNKNOWN = "UNKNOWN"
    NEW = "NEW"
    PAID = "PAID"
    CANCELLED = "CANCELLED"

    @classmethod
    def to_choices(cls) -> List[Tuple]:
        return [(e.value, e.name) for e in cls]


class SubscriptionEntity(BaseModel):
    invoice_id : str = None
    customer_id : str = None
    product_id : str = None
    status: str  = None
    price : int = 0
    currency : str = "usd"
    payment_frequency : str = "month"
    purchase_date : datetime = None
    payment_status : str = None
    subscription_id : str = None
    expires_at : datetime = None
    canceled_at : Optional[datetime] = None


class CheckoutCreationEntity(BaseModel):
    price_id: str
    mode: str = "subscription"
    ui_mode: str = "embed"
    redirect_url: str = ""
