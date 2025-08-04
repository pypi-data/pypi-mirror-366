from dataclasses import dataclass
from fmconsult.utils.object import CustomObject

@dataclass
class CreditCardInfo(CustomObject):
  holderName:str
  number:str
  expiryMonth:str
  expiryYear:str
  ccv:str

@dataclass
class CreditCardHolderInfo(CustomObject):
  name:str
  email:str
  cpfCnpj:str
  postalCode:str
  address:str
  addressNumber:str
  addressComplement:str
  city:str
  uf:str
  phone:str
  mobilePhone:str

@dataclass
class CreditCard(CustomObject):
  customer:str
  creditCard:CreditCardInfo
  creditCardHolderInfo:CreditCardHolderInfo
  remoteIp:str