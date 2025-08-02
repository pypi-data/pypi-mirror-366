from dataclasses import dataclass
from typing import Optional
from fmconsult.utils.object import CustomObject

@dataclass
class Split(CustomObject):
    recipient_account_id: str
    cents: int
    percent: float
    permit_aggregated: bool
    bank_slip_cents: int
    bank_slip_percent: float
    credit_card_cents: int
    credit_card_percent: float
    pix_cents: int
    pix_percent: float
    credit_card_1x_cents: int
    credit_card_2x_cents: int
    credit_card_3x_cents: int
    credit_card_4x_cents: int
    credit_card_5x_cents: int
    credit_card_6x_cents: int
    credit_card_7x_cents: int
    credit_card_8x_cents: int
    credit_card_9x_cents: int
    credit_card_10x_cents: int
    credit_card_11x_cents: int
    credit_card_12x_cents: int
    credit_card_1x_percent: float
    credit_card_2x_percent: float
    credit_card_3x_percent: float
    credit_card_4x_percent: float
    credit_card_5x_percent: float
    credit_card_6x_percent: float
    credit_card_7x_percent: float
    credit_card_8x_percent: float
    credit_card_9x_percent: float
    credit_card_10x_percent: float
    credit_card_11x_percent: float
    credit_card_12x_percent: float

@dataclass
class KeyValue(CustomObject):
    name: str
    value: str

@dataclass
class Subscription(CustomObject):
    customer_id: str
    plan_identifier: Optional[str]
    expires_at: Optional[str]
    splits: Optional[list[Split]]
    only_on_charge_success: Optional[bool]
    ignore_due_email: Optional[bool]
    payable_with: Optional[list[str]]
    credits_based: Optional[bool]
    price_cents: Optional[int]
    credits_cycle: Optional[int]
    credits_min: Optional[int]
    custom_variables: Optional[list[KeyValue]]
    two_step: Optional[bool]
    suspend_on_invoice_expired: Optional[bool]
    only_charge_on_due_date: Optional[bool]
    soft_descriptor_light: Optional[str]
    return_url: Optional[str]