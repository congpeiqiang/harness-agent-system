"""
@File    :  config.py
@Author  :  CongPeiQiang
@Time    :  2026/6/8 21:04
@Desc    :  
"""
import os
from typing import Dict, Any


class FecMallConfig:
    def __init__(self):
        self.settings = {
            # 'base_url': os.getenv('FECMALL_BASE_URL', 'https://appserver.huice.com'),
            'base_url': 'http://appserver.huice.com',
            'timeout': int(os.getenv('FECMALL_TIMEOUT', '30')),
            'max_retries': int(os.getenv('FECMALL_MAX_RETRIES', '3'))
        }

    def get_setting(self, key: str, default: Any = None) -> Any:
        print(self.settings)
        return self.settings.get(key, default)

    def update_setting(self, key: str, value: Any) -> None:
        self.settings[key] = value
