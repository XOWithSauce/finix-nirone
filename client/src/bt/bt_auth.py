import base64
import os
import hashlib
import hmac
import binascii
import json
from Crypto.Cipher import AES

class HmacAuth:
    def __init__(self, shared_sig_key) -> None:
        self.__shared_sig_key = str(shared_sig_key).encode()

    def __gen_signature(self, message: bytes) -> str:
        k = self.__shared_sig_key
        h = hmac.new(k, message, hashlib.sha256).hexdigest()
        return h
    
    def ask_for_signature(self, message: bytes) -> str:
        s = self.__gen_signature(message)
        return s
    
    def compare_digest(self, recv_sign: str, gen_sign: str) -> bool:
        return hmac.compare_digest(recv_sign, gen_sign)
    
class AesEncryption:
    def __init__(self, shared_encr_key) -> None:
        self.__shared_encr_key = str(shared_encr_key).encode()
    
    def __gen_ciphertext(self, message: bytes, iv: bytes) -> bytes:
        ec = AES.new(self.__shared_encr_key, AES.MODE_CBC, iv)
        pad = AES.block_size - len(message) % AES.block_size
        message = message + bytes([pad]) * pad
        ct = ec.encrypt(message)
        return ct

    def __dec_message(self, ciphertext: bytes, iv: bytes) -> bytes:
        dc = AES.new(self.__shared_encr_key, AES.MODE_CBC, iv)
        m = dc.decrypt(ciphertext)
        pad = m[-1]
        return m[:-pad]
    
    def ask_to_encrypt(self, message: str, iv: bytes) -> bytes:
        e = self.__gen_ciphertext(message.encode(), iv)
        return e
    
    def ask_to_decrypt(self, message: bytes, iv: bytes) -> str:
        m = self.__dec_message(message, iv)
        m = m.decode()
        return m
    
class BTAuth:
    def __init__(self, shared_sig_key, shared_encr_key) -> None:
        # Compose the classes
        self.auth_hmac = HmacAuth(shared_sig_key)
        self.auth_encr = AesEncryption(shared_encr_key)

    def encrypt_message(self, message: str) -> str:
        print("ENCRYPT")
        #iv = bytes(16)
        iv = os.urandom(16)
        encrypted_message = self.auth_encr.ask_to_encrypt(message, iv)
        signature = self.auth_hmac.ask_for_signature(encrypted_message)
        encrypted_message = binascii.b2a_base64(encrypted_message, newline=False).decode()
        iv = binascii.b2a_base64(iv, newline=False).decode()
        result = json.dumps({"signature": signature, "message": encrypted_message, "iv": iv})
        return result
    
    def decrypt_message(self, signed_message: str) -> str:
        decrypted_message = ""
        # JSON String Deserialization to Dict object
        message_dict = json.loads(signed_message)
        print("\nDECRYPT: ", message_dict)
        recv_signature: str = message_dict["signature"]
        encrypted_message_bytes: bytes = base64.b64decode(message_dict["message"])
        iv_bytes: bytes = base64.b64decode(message_dict["iv"])
        
        # Decryption
        try:
            gen_sign = self.auth_hmac.ask_for_signature(encrypted_message_bytes)
            
            # If signature matches, proceed to decrypt message content
            if(self.auth_hmac.compare_digest(recv_signature, gen_sign)):
                decrypted_message = self.auth_encr.ask_to_decrypt(
                    encrypted_message_bytes, 
                    iv_bytes
                    )
            else:
                print("Warning: Signature did not match. Message has been modified mid-traffic!")
                print("Generated: ", gen_sign)
                print("Received: ", recv_signature)
        except:
            decrypted_message = ""
            
        return decrypted_message

def main():
    # Define the shared keys (example 256 Bits)
    # NOTE: Do not keep keys in code, always adhere to best practices.
    shared_sig_key = "HopeGatheringSubstitutionWestRow"
    shared_encr_key = "ModalTerritoryAlligatorCyanNorth"

    # Initialize the Encryption example
    encryption_example = BTAuth(shared_sig_key, shared_encr_key)

    # Define a message that you want to send
    message = "kk"
    
    # Encrypting the message
    result = encryption_example.encrypt_message(message)
    print(type(result))
    # Now we can see that the result contains signature created from encrypted message,
    # the encrypted message and the iv needed for decryption.
    print(result)
    
    # Decrypting and verifying signature
    decrypted_message = encryption_example.decrypt_message(result)
    print("\nDecrypted message: ", decrypted_message ,"\n")
    return

if __name__ == "__main__":
    main()