from dataclasses import dataclass
from typing import Optional
from fmconsult.utils.object import CustomObject

@dataclass
class Customer(CustomObject):
    email: str
    name: str
    phone: Optional[int]
    phone_prefix: Optional[int]
    cpf_cnpj: Optional[str]
    zip_code: Optional[str]
    number: Optional[str]
    street: Optional[str]
    city: Optional[str]
    state: Optional[str]
    district: Optional[str]
    complement: Optional[str]