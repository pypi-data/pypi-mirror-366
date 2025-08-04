import logging, jsonpickle
from http import HTTPMethod
from fmconsult.utils.url import UrlUtil
from asaas.api import AsaasApi
from asaas.dtos.customer import Customer, Filter

class Customers(AsaasApi):
  
  def __init__(self):
    super().__init__()
    self.endpoint_url = UrlUtil().make_url(self.base_url, ['v3', 'customers'])

  def create(self, data:Customer):
    try:
      logging.info(f'generating customer...')
      res = self.call_request(HTTPMethod.POST, self.endpoint_url, None, payload=data.__dict__)
      return jsonpickle.decode(res)
    except:
      raise

  def update(self, id, data:Customer):
   try:
      logging.info(f'updating customer...')
      self.endpoint_url = UrlUtil().make_url(self.endpoint_url, [id])
      res = self.call_request(HTTPMethod.PUT, self.endpoint_url, None, payload=data.__dict__)
      return jsonpickle.decode(res)
   except:
      raise

  def remove(self, id):
    try:
      logging.info(f'delete customer by id: {id}...')
      self.endpoint_url = UrlUtil().make_url(self.endpoint_url, [id])
      res = self.call_request(HTTPMethod.DELETE, self.endpoint_url)
      return jsonpickle.decode(res)
    except:
      raise
  
  def get_all(self, filters:Filter):
    try:
      logging.info(f'listing customers...')
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
      logging.info(f'get customer info by id: {id}...')
      self.endpoint_url = UrlUtil().make_url(self.endpoint_url, [id])
      res = self.call_request(HTTPMethod.GET, self.endpoint_url)
      return jsonpickle.decode(res)
   except:
     raise
