from dataclasses import dataclass
from typing import Optional
from fmconsult.utils.enum import CustomEnum
from fmconsult.utils.object import CustomObject

@dataclass
class Filter(CustomObject):
  cpfCnpj: str
  email: str
  name: str
  walletId: str
  offset: int
  limit: int

class CompanyType(CustomEnum):
  MEI = 'MEI'
  LIMITED = 'LIMITED'
  INDIVIDUAL = 'INDIVIDUAL'
  ASSOCIATION = 'ASSOCIATION'

@dataclass
class Account(CustomObject):
  name: str
  email: str
  cpfCnpj: str
  birthDate: str
  mobilePhone: str
  incomeValue: float
  address: str
  addressNumber: str
  complement: str
  province: str
  postalCode: str
  loginEmail: Optional[str] = None
  companyType: Optional[CompanyType] = None
  phone: Optional[str] = None
  site: Optional[str] = None