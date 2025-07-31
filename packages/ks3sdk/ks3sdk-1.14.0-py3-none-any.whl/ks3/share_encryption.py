import os
import logging
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import SHA256
import base64
import ks3
logger = logging.getLogger(__name__)

PBKDF2_ITER = 10000
PBKDF2_KEY_LENGTH = 32
TOKEN_SEPARATOR = "_"
IV = 'ks3-share12345v1'


def parse_token(token, access_code):
    result_arr = token.split(TOKEN_SEPARATOR)
    code = result_arr[0]
    logger.debug(f"token: {token}")
    salt = base64.b64decode(result_arr[1])
    iv = base64.b64decode(result_arr[2])
    logger.debug(f"encrypted_b64: {code}, salt_b64: {result_arr[1]}, iv_b64: {result_arr[2]}")
    key = PBKDF2(access_code, salt, dkLen=PBKDF2_KEY_LENGTH, count=PBKDF2_ITER, hmac_hash_module=SHA256)
    logger.debug(f"PBKDF2 key: {key.hex()}, iv: {iv}")
    return {
        'authCode': code,
        'key': key,
        'iv': iv
    }


class ShareCryptor(object):
    def __init__(self, access_code):
        """
        This encryption class use AES.CBC MODE(128 bit) as default.
        @param access_code: 分享码
        """
        self.access_code = access_code

    def decrypt(self, token_params):
        logger.debug('\ndecrypting...')
        # share_token = token_params[9:]
        share_token = token_params
        token_params = parse_token(share_token, self.access_code)
        if not token_params:
            return ''
        share_token = token_params['authCode']
        key = token_params['key']
        iv = token_params['iv']

        try:
            cipher = AES.new(key, AES.MODE_CBC, iv=iv)
            decoded_token = base64.b64decode(share_token)
            logger.debug(f'encrypted: ${decoded_token.hex()}')
            decrypted = cipher.decrypt(decoded_token)
            logger.debug(f'padded_content: ${decrypted}')
            unpad_content = unpad(decrypted, AES.block_size, style='pkcs7').decode('utf-8')
            logger.debug(f'unpad_content: ${unpad_content}')
            url = base64.b64decode(unpad_content).decode('utf-8')
        except Exception as e:
            raise ValueError("Decryption failed")

        return url

    def encrypt(self, value, salt=None, iv=None):
        logger.debug('encrypting...')
        logger.debug(f'content before base64: {value}')
        content = base64.b64encode(value.encode('utf-8')).decode('utf-8')
        if salt is None:
            salt = b'ks3-share12345v1'
        if iv is None:
            iv = IV.encode('utf-8')
        logger.debug(f"access_code: {self.access_code}, content: {content}, salt: {salt}, iv: {iv}")
        key = PBKDF2(self.access_code, salt, dkLen=PBKDF2_KEY_LENGTH, count=PBKDF2_ITER, hmac_hash_module=SHA256)
        logger.debug(f"PBKDF2 key: {key.hex()}")
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        padded_content = pad(content.encode('utf-8'), AES.block_size, style='pkcs7')
        logger.debug(f"padded_content: {padded_content}")
        encrypted = cipher.encrypt(padded_content)
        logger.debug(f"encrypted: {encrypted.hex()}")
        encrypted_b64 = base64.b64encode(encrypted).decode('utf-8')
        salt_b64 = base64.b64encode(salt).decode('utf-8')
        iv_b64 = base64.b64encode(iv).decode('utf-8')
        logger.debug(f"encrypted_b64: {encrypted_b64}, salt_b64: {salt_b64}, iv_b64: {iv_b64}")
        return f"{encrypted_b64}_{salt_b64}_{iv_b64}"
