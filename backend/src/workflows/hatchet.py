
from hatchet_sdk import Hatchet
import os

from ..config import settings

os.environ["HATCHET_CLIENT_TOKEN"] = settings.hatchet_client_token

hatchet = Hatchet()
