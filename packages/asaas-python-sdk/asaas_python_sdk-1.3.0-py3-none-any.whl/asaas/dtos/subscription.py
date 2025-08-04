from dataclasses import dataclass
from typing import List, Optional
from .credit_card import CreditCardInfo, CreditCardHolderInfo
from fmconsult.utils.object import CustomObject
from fmconsult.utils.enum import CustomEnum

class CycleTypes(CustomEnum):
  WEEKLY        = "WEEKLY"
  BIWEEKLY      = "BIWEEKLY"
  MONTHLY       = "MONTHLY"
  BIMONTHLY     = "BIMONTHLY"
  QUARTERLY     = "QUARTERLY"
  SEMIANNUALLY  = "SEMIANNUALLY"
  YEARLY        = "YEARLY"

class BillingType(CustomEnum):
  UNDEFINED = "UNDEFINED"
  BOLETO = "BOLETO"
  CREDIT_CARD = "CREDIT_CARD"
  PIX = "PIX"

@dataclass
class Filter(CustomObject):
  customer:str
  customerGroupName:str
  billingType:str
  status:str
  deletedOnly:bool
  includeDeleted:bool
  externalReference:str
  order:str
  sort:str
  offset:int
  limit:int

@dataclass
class Split(CustomObject):
  walletId:str
  fixedValue:float
  percentualValue:float

@dataclass
class Subscription(CustomObject):
  customer:str
  billingType:BillingType
  value:float
  nextDueDate:str
  cycle:CycleTypes
  description:str
  externalReference:str
  creditCard: Optional[CreditCardInfo] = None
  creditCardHolderInfo: Optional[CreditCardHolderInfo] = None
  split: Optional[List[Split]] = None
  remoteIp: Optional[str] = None
  endDate: Optional[str] = None