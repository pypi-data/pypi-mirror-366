import logging, jsonpickle
from http import HTTPMethod
from fmconsult.utils.url import UrlUtil
from asaas.api import AsaasApi
from asaas.dtos.webhook import Webhook

class Webhooks(AsaasApi):

  def __init__(self):
    super().__init__()
    self.endpoint_url = UrlUtil().make_url(self.base_url, ['v3', 'webhooks'])

  def create(self, data:Webhook):
    try:
      logging.info(f'generating webhook...')
      res = self.call_request(HTTPMethod.POST, self.endpoint_url, None, payload=data.to_dict())
      return jsonpickle.decode(res)
    except:
      raise