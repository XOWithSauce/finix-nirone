import hashlib
import hmac
from env import ENV
# MODULE IMPORT
from datetime import datetime, timezone


class HmacAuth:
    def __init__(self) -> None:
        # NOTE: MAKE SURE NOTIFY KEY IS NOT NONE!!!
        self.__shared_key = str(ENV.SHARED_KEY).encode()
        pass

    def __gen_signature(self, message: bytes) -> str:
        k = self.__shared_key
        h = hmac.new(k, message, hashlib.sha256).hexdigest()
        return h
    
    def ask_for_headers(self, message: str) -> dict:
        signature = self.__gen_signature(message.encode())
        headers = {
            "X-Hmac-Sig": signature,
            "Content-Type": "application/json",
            }
        return headers
