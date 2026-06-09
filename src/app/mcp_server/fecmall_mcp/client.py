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

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None,  return_full: bool = False) -> Dict:
        url = f"{self.config.get_setting('base_url')}/{endpoint}"
        # 如果有 access_token，添加到请求头中
        if "access_token" in data:
            self.session.headers.update({"Access-Token": data["access_token"]})
        for attempt in range(self.config.get_setting('max_retries')):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    data=data,
                    timeout=self.config.get_setting('timeout')
                )
                response.raise_for_status()
                if return_full:
                    response_json = response.json()
                    # 从响应headers中获取access_token
                    if response and hasattr(response, 'headers') and 'Access-Token' in response.headers:
                        headers = getattr(response, 'headers', {})
                        access_token = headers.get('Access-Token', None)
                        if access_token:
                            temp_dict = {"Access-Token": access_token}
                            response_json["data"].append(temp_dict)
                    return response_json
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == self.config.get_setting('max_retries') - 1:
                    raise e
                continue

# config = FecMallConfig()
# print(f"config: {config.settings}")
# client = FecMallClient(config)
# response_json = client.make_request("POST", "customer/login/account", data={'email': '1539397039@qq.com', 'password': '123456'}, return_full=True)
# response_json = client.make_request("POST", "customer/address/index", data={'access_token': 'YCAB36smz7Ol5WT9kJUXKyW87aV-gIoA'})
# print(f"response_json: {response_json}")