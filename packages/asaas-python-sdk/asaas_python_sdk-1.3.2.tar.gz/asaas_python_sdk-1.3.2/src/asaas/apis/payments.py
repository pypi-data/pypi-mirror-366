import logging, jsonpickle
from enum import Enum
from http import HTTPMethod
from fmconsult.utils.url import UrlUtil
from asaas.api import AsaasApi
from asaas.dtos.payment import Filter

class Status(Enum):
  PENDING = 'PENDING'
  RECEIVED = 'RECEIVED'
  CONFIRMED = 'CONFIRMED'
  OVERDUE = 'OVERDUE'
  REFUNDED = 'REFUNDED'
  RECEIVED_IN_CASH = 'RECEIVED_IN_CASH'
  REFUND_REQUESTED = 'REFUND_REQUESTED'
  REFUND_IN_PROGRESS = 'REFUND_IN_PROGRESS'
  CHARGEBACK_REQUESTED = 'CHARGEBACK_REQUESTED'
  CHARGEBACK_DISPUTE = 'CHARGEBACK_DISPUTE'
  AWAITING_CHARGEBACK_REVERSAL = 'AWAITING_CHARGEBACK_REVERSAL'
  DUNNING_REQUESTED = 'DUNNING_REQUESTED'
  DUNNING_RECEIVED = 'DUNNING_RECEIVED'
  AWAITING_RISK_ANALYSIS = 'AWAITING_RISK_ANALYSIS'

class Payments(AsaasApi):

  def __init__(self):
    super().__init__()
    self.endpoint_url = UrlUtil().make_url(self.base_url, ['v3', 'payments'])

  def confirmReceiveInCash(self, payment_id, payment_date, value, notify_customer=True):
    try:
      logging.info(f'confirm receive in cash...')
      endpoint_url = UrlUtil().make_url(self.endpoint_url, [payment_id, 'receiveInCash'])
      payload = {
          'paymentDate': payment_date,
          'value': value,
          'notifyCustomer': notify_customer
      }
      res = self.call_request(HTTPMethod.POST, endpoint_url, None, payload)
      return jsonpickle.decode(res)
    except:
      raise
  
  def get_all(self, filters:Filter):
    try:
      logging.info(f'listing payments...')
      if not filters is None:
        params = {field: value for field, value in vars(filters).items() if value is not None}
      else:
        params = {}
      res = self.call_request(HTTPMethod.GET, self.endpoint_url, params=params)
      return jsonpickle.decode(res)
    except:
      raise
  
  def get_by_id(self, payment_id):
    try:
      logging.info(f'get payment by id...')
      endpoint_url = UrlUtil().make_url(self.endpoint_url, [payment_id])
      res = self.call_request(HTTPMethod.GET, endpoint_url)
      return jsonpickle.decode(res)
    except:
      raise
  
  def get_status_by_id(self, payment_id):
    try:
      logging.info(f'get payment by id...')
      endpoint_url = UrlUtil().make_url(self.endpoint_url, [payment_id, 'status'])
      res = self.call_request(HTTPMethod.GET, endpoint_url)
      return jsonpickle.decode(res)
    except:
      raise

  def get_qrcode_pix(self, payment_id):
    try:
      logging.info(f'get payment PIX QRCode by id...')
      endpoint_url = UrlUtil().make_url(self.endpoint_url, [payment_id, 'pixQrCode'])
      res = self.call_request(HTTPMethod.GET, endpoint_url)
      return jsonpickle.decode(res)
    except:
      raise