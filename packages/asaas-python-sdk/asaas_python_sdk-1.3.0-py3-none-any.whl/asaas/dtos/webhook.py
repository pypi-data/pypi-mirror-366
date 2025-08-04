from dataclasses import dataclass, asdict, is_dataclass
from enum import Enum
from typing import List
from fmconsult.utils.enum import CustomEnum
from fmconsult.utils.object import CustomObject

class SendType(CustomEnum):
  SEQUENTIALLY = 'SEQUENTIALLY'
  NON_SEQUENTIALLY = 'NON_SEQUENTIALLY'

@dataclass
class Webhook(CustomObject):
  name: str
  url: str
  email: str
  events: List[str]
  enabled: bool = True
  authToken: str = None
  apiVersion: str = "3"
  interrupted: bool = False
  sendType: SendType = SendType.SEQUENTIALLY

  def to_dict(self):
    def convert_value(value):
      if isinstance(value, Enum):
        return value.value
      elif is_dataclass(value):
        return {k: convert_value(v) for k, v in asdict(value).items()}
      elif isinstance(value, list):
        return [convert_value(v) for v in value]
      elif isinstance(value, dict):
        return {k: convert_value(v) for k, v in value.items()}
      else:
        return value

    return {k: convert_value(v) for k, v in asdict(self).items()}
