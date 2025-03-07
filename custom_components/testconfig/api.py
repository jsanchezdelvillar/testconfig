import asyncio
import json
import random
import string
import time
import aiohttp
import logging

from .encryption import public_encrypt, encrypt, decrypt, generate_nonce
from .const import CONF_USERNAME, CONF_PASSWORD, CONF_APPKEY, CONF_X_ACCESS_KEY, CONF_PUBLIC_KEY, CONF_PS_KEY, CONF_POINT_ID_LIST

_LOGGER = logging.getLogger(__name__)

class SolarAPI:
    def __init__(self, hass, config):
        self.hass = hass
        self.session = aiohttp.ClientSession()
        self.username = config[CONF_USERNAME]
        self.password = config[CONF_PASSWORD]
        self.appkey = config[CONF_APPKEY]
        self.x_access_key = config[CONF_X_ACCESS_KEY]
        self.public_key_base64 = config[CONF_PUBLIC_KEY]
        self.ps_key = config[CONF_PS_KEY]
        self.point_id_list = config[CONF_POINT_ID_LIST]
        self.token = None
    
    async def authenticate(self):
        """Obtain a new authentication token."""
        login_url = "https://gateway.isolarcloud.eu/openapi/login"
        unenc_x_random_secret_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        x_random_secret_key = public_encrypt(unenc_x_random_secret_key, self.public_key_base64)
        nonce = generate_nonce()
        timestamp = str(int(time.time() * 1000))
        
        login_payload = {
            "api_key_param": {"nonce": nonce, "timestamp": timestamp},
            "appkey": self.appkey,
            "login_type": "1",
            "user_account": self.username,
            "user_password": self.password
        }
        
        login_headers = {
            "User-Agent": "Home Assistant",
            "x-access-key": self.x_access_key,
            "x-random-secret-key": x_random_secret_key,
            "Content-Type": "application/json",
            "sys_code": "901"
        }
        
        encrypted_request_body = encrypt(json.dumps(login_payload), unenc_x_random_secret_key)
        
        async with self.session.post(login_url, headers=login_headers, data=encrypted_request_body) as response:
            if response.status == 200:
                response_body = await response.text()
                decrypted_response_body = decrypt(response_body, unenc_x_random_secret_key)
                response_json = json.loads(decrypted_response_body)
                if response_json.get("result_code") == "1" and response_json.get("result_data", {}).get("login_state") == "1":
                    self.token = response_json["result_data"].get("token", "")
                    return self.token
            return None

    async def get_device_data(self):
        """Obtain real-time device data."""
        if not self.token:
            await self.authenticate()
        
        device_data_url = "https://gateway.isolarcloud.eu/openapi/getDeviceRealTimeData"
        unenc_x_random_secret_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        x_random_secret_key = public_encrypt(unenc_x_random_secret_key, self.public_key_base64)
        nonce = generate_nonce()
        timestamp = str(int(time.time() * 1000))
        
        headers = {
            "User-Agent": "Home Assistant",
            "x-access-key": self.x_access_key,
            "x-random-secret-key": x_random_secret_key,
            "Content-Type": "application/json",
            "token": self.token,
            "sys_code": "901"
        }
        
        device_data_payload = {
            "api_key_param": {"nonce": nonce, "timestamp": timestamp},
            "appkey": self.appkey,
            "device_type": 11,
            "point_id_list": self.point_id_list,
            "ps_key_list": [self.ps_key]
        }
        
        encrypted_request_body = encrypt(json.dumps(device_data_payload), unenc_x_random_secret_key)
        
        async with self.session.post(device_data_url, headers=headers, data=encrypted_request_body) as response:
            if response.status == 200:
                response_body = await response.text()
                decrypted_response_body = decrypt(response_body, unenc_x_random_secret_key)
                return json.loads(decrypted_response_body)
            return None
