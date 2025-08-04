from dataclasses import dataclass, asdict
from typing import Optional
from fmconsult.utils.object import CustomObject

@dataclass
class Filter(CustomObject):
  customer: Optional[str] = None
  customerGroupName: Optional[str] = None
  billingType: Optional[str] = None
  status: Optional[str] = None
  subscription: Optional[str] = None
  installment: Optional[str] = None
  externalReference: Optional[str] = None
  paymentDate: Optional[str] = None
  invoiceStatus: Optional[str] = None
  estimatedCreditDate: Optional[str] = None
  pixQrCodeId: Optional[str] = None
  anticipated: Optional[str] = None
  dateCreated__ge: Optional[str] = None
  dateCreated__le: Optional[str] = None
  paymentDate__ge: Optional[str] = None
  paymentDate__le: Optional[str] = None
  estimatedCreditDate__ge: Optional[str] = None
  estimatedCreditDate__le: Optional[str] = None
  dueDate__ge: Optional[str] = None
  dueDate__le: Optional[str] = None
  user: Optional[str] = None
  offset: Optional[int] = 0
  limit: Optional[int] = 10

  def to_dict(self):
    data = asdict(self)
    
    data['dateCreated[ge]'] = self.dateCreated__ge
    data['dateCreated[le]'] = self.dateCreated__le
    data['paymentDate[ge]'] = self.paymentDate__ge
    data['paymentDate[le]'] = self.paymentDate__le
    data['estimatedCreditDate[ge]'] = self.estimatedCreditDate__ge
    data['estimatedCreditDate[le]'] = self.estimatedCreditDate__le
    data['dueDate[ge]'] = self.dueDate__ge
    data['dueDate[le]'] = self.dueDate__le

    return data