import logging, jsonpickle
from http import HTTPMethod
from fmconsult.utils.url import UrlUtil
from asaas.api import AsaasApi
from asaas.dtos.credit_card import CreditCard

class CreditCards(AsaasApi):

  def __init__(self):
    super().__init__()
    self.endpoint_url = UrlUtil().make_url(self.base_url, ['v3', 'creditCard'])

  def tokenize(self, data:CreditCard):
   try:
      logging.info(f'generating account...')
      self.endpoint_url = UrlUtil().make_url(self.endpoint_url, ['tokenize'])
      res = self.call_request(HTTPMethod.POST, self.endpoint_url, None, payload=data.__dict__)
      return jsonpickle.decode(res)
   except:
     raise
