"""
@File    :  client.py
@Author  :  CongPeiQiang
@Time    :  2026/6/8 21:04
@Desc    :  
"""
import requests
from typing import Dict, Any, Optional
from .config import FecMallConfig


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

        for attempt in range(self.config.get_setting('max_retries')):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    timeout=self.config.get_setting('timeout')
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == self.config.get_setting('max_retries') - 1:
                    raise e
                continue
