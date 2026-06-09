"""
@File    :  onepage.py
@Author  :  CongPeiQiang
@Time    :  2026/6/9
@Desc    :  结账页面API工具
"""
from typing import Dict, Any
from app.mcp_server.fecmall_mcp.client import FecMallClient


def get_onepage_info(client: FecMallClient, access_token: str) -> Dict[str, Any]:
    """
    获取结账页面信息
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
    Returns:
        Dict: 结账页面信息
    """
    endpoint = "checkout/onepage/index"
    data = {
        "access_token": access_token
    }
    return client.make_request("GET", endpoint, data)


def change_onepage_country(
    client: FecMallClient,
    access_token: str,
    country: str
) -> Dict[str, Any]:
    """
    更改结账页面国家
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
        country: 国家代码
    Returns:
        Dict: 国家更改结果
    """
    endpoint = "checkout/onepage/changecountry"
    data = {
        "access_token": access_token,
        "country": country
    }
    return client.make_request("POST", endpoint, data)


def update_onepage_info(
    client: FecMallClient,
    access_token: str,
    address_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    更新结账页面信息
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
        address_data: 地址、配送方式、支付方式等信息
    Returns:
        Dict: 更新结果
    """
    endpoint = "checkout/onepage/getshippingandcartinfo"
    data = {
        "access_token": access_token,
        **address_data
    }
    return client.make_request("POST", endpoint, data)
