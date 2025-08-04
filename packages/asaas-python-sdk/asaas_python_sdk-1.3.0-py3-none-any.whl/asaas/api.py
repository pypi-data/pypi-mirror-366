import os
from fmconsult.http.api import ApiBase

class AsaasApi(ApiBase):

  def __init__(self):
    try:
      self.access_token = os.environ['asaas.api.access_token']
      
      api_sandbox_base_url = 'https://sandbox.asaas.com/api'
      api_live_base_url = 'https://api.asaas.com'

      get_base_url = lambda env: api_live_base_url if env == 'live' else api_sandbox_base_url

      self.api_environment = os.environ['asaas.api.environment']
      self.base_url = get_base_url(self.api_environment)
      self.headers = {
        'access_token': self.access_token
      }
    except:
      raise
  