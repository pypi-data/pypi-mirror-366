from dataclasses import dataclass
from typing import Optional
from fmconsult.utils.object import CustomObject

@dataclass
class Filter(CustomObject):
  name:str
  email:str
  cpfCnpj:str
  groupName:str
  externalReference:str
  offset:int
  limit:int

@dataclass
class Customer(CustomObject):
  name:str
  cpfCnpj:str
  email: Optional[str] = None
  phone: Optional[str] = None
  mobilePhone: Optional[str] = None
  address: Optional[str] = None
  addressNumber: Optional[str] = None
  complement: Optional[str] = None
  province: Optional[str] = None
  postalCode: Optional[str] = None
  externalReference: Optional[str] = None
  notificationDisabled: Optional[bool] = None
  additionalEmails: Optional[str] = None
  municipalInscription: Optional[str] = None
  stateInscription: Optional[str] = None
  observations: Optional[str] = None
  groupName: Optional[str] = None
  company: Optional[str] = None