"""
@File    :  client.py
@Author  :  CongPeiQiang
@Time    :  2026/6/8 21:04
@Desc    :  
"""
import requests
from typing import Dict, Any, Optional
from app.mcp_server.fecmall_mcp.config import FecMallConfig


class FecMallClient:
    def __init__(self, config: FecMallConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            # 'Content-Type': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        })

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        url = f"{self.config.get_setting('base_url')}/{endpoint}"
        print(f"请求-2: {url}")
        for attempt in range(self.config.get_setting('max_retries')):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    data=data,
                    timeout=self.config.get_setting('timeout')
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == self.config.get_setting('max_retries') - 1:
                    raise e
                continue

# config = FecMallConfig()
# print(f"config: {config.settings}")
# client = FecMallClient(config)
# response_json = client.make_request("POST", "customer/login/account", data={'email': '1539397039@qq.com', 'password': '123456'})
# print(f"response_json: {response_json}")