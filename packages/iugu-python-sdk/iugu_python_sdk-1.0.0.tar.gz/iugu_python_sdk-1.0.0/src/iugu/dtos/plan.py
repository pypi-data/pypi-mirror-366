from dataclasses import dataclass
from typing import Optional
from fmconsult.utils.enum import CustomEnum
from fmconsult.utils.object import CustomObject

class IntervalType(CustomEnum):
    MONTHS = "months"
    WEEKS = "weeks"

@dataclass
class Plan(CustomObject):
  name: str
  identifier: str
  interval: int
  interval_type: str[IntervalType]
  value_cents: float
  payable_with: list[str]
  billing_days: Optional[int]