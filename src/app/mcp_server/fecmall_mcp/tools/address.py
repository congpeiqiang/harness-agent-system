"""
@File    :  address.py
@Author  :  CongPeiQiang
@Time    :  2026/6/8
@Desc    :  地址管理API工具（合并address_detail.py）
"""
from typing import Dict, Any
from app.mcp_server.fecmall_mcp.client import FecMallClient


def get_customer_addresses(client: FecMallClient, access_token: str) -> Dict[str, Any]:
    """
    获取客户地址列表
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
    Returns:
        Dict: 地址列表
    """
    endpoint = "customer/address/index"
    data = {
        "access_token": access_token
    }
    return client.make_request("GET", endpoint, data)


def get_address_info(
    client: FecMallClient,
    access_token: str,
    address_id: str
) -> Dict[str, Any]:
    """
    获取地址详情（初始化编辑页面）
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
        address_id: 地址ID
    Returns:
        Dict: 地址详情
    """
    endpoint = "customer/address/edit"
    data = {
        "access_token": access_token,
        "address_id": address_id
    }
    return client.make_request("GET", endpoint, data)


def change_address_country(
    client: FecMallClient,
    access_token: str,
    country: str
) -> Dict[str, Any]:
    """
    更改地址国家（编辑页联动获取省/州信息）
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
        country: 国家代码
    Returns:
        Dict: 国家更改结果
    """
    endpoint = "customer/address/changecountry"
    data = {
        "access_token": access_token,
        "country": country
    }
    return client.make_request("POST", endpoint, data)


def save_customer_address(
    client: FecMallClient,
    access_token: str,
    address_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    保存地址（添加新地址或更新已有地址）
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
        address_data: 地址数据，包含：
                      - address_id: 可选，有则更新，无则添加
                      - first_name, last_name, email, telephone
                      - street1, street2, city, state, country, zip
                      - is_default: 是否设为默认地址
    Returns:
        Dict: 保存结果
    """
    endpoint = "customer/address/save"
    data = {
        "access_token": access_token,
        **address_data
    }
    return client.make_request("POST", endpoint, data)


def remove_customer_address(
    client: FecMallClient,
    access_token: str,
    address_id: str
) -> Dict[str, Any]:
    """
    删除客户地址
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
        address_id: 地址ID
    Returns:
        Dict: 删除结果
    """
    endpoint = "customer/address/remove"
    data = {
        "access_token": access_token,
        "address_id": address_id
    }
    return client.make_request("GET", endpoint, data)
