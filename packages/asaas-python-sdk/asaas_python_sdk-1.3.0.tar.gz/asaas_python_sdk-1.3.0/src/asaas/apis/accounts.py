import logging, jsonpickle
from http import HTTPMethod
from fmconsult.utils.url import UrlUtil
from asaas.api import AsaasApi
from asaas.dtos.account import Account, Filter

class Accounts(AsaasApi):

  def __init__(self):
    super().__init__()
    self.endpoint_url = UrlUtil().make_url(self.base_url, ['v3', 'accounts'])

  def create(self, data:Account):
    try:
      logging.info(f'generating account...')
      res = self.call_request(HTTPMethod.POST, self.endpoint_url, None, payload=data.__dict__)
      return jsonpickle.decode(res)
    except:
      raise
  
  def get_all(self, filters:Filter):
    try:
      logging.info(f'listing accounts...')
      if not filters is None:
        params = {field: value for field, value in vars(filters).items() if value is not None}
      else:
        params = {}
      res = self.call_request(HTTPMethod.GET, self.endpoint_url, params=params)
      return jsonpickle.decode(res)
    except:
      raise

  def get_by_id(self, id):
    try:
      logging.info(f'get account info by id: {id}...')
      params = {
        'id': id
      }
      res = self.call_request(HTTPMethod.GET, self.endpoint_url, params=params)
      return jsonpickle.decode(res)
    except:
      raise
