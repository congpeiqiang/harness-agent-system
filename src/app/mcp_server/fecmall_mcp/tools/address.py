"""
@File    :  address.py
@Author  :  CongPeiQiang
@Time    :  2026/6/8 21:05
@Desc    :  
"""
from typing import Dict, Any
from app.mcp_server.fecmall_mcp.client import FecMallClient

def add_customer_address(client: FecMallClient, access_token: str, address_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    添加客户地址
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
        address_data: 地址信息字典
    Returns:
        Dict: 添加地址结果
    """
    endpoint = "customer/address"
    data = {
        "access_token": access_token,
        **address_data
    }
    return client.make_request("POST", endpoint, data)

def update_customer_address(client: FecMallClient, access_token: str, address_id: str, address_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    更新客户地址
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
        address_id: 地址ID
        address_data: 地址信息字典
    Returns:
        Dict: 更新地址结果
    """
    endpoint = f"customer/address/{address_id}"
    data = {
        "access_token": access_token,
        **address_data
    }
    return client.make_request("PUT", endpoint, data)

def get_customer_addresses(client: FecMallClient, access_token: str) -> Dict[str, Any]:
    """
    获取客户地址列表
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
    Returns:
        Dict: 地址列表
    """
    endpoint = "customer/address"
    data = {
        "access_token": access_token
    }
    return client.make_request("GET", endpoint, data)

def remove_customer_address(client: FecMallClient, access_token: str, address_id: str) -> Dict[str, Any]:
    """
    删除客户地址
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
        address_id: 地址ID
    Returns:
        Dict: 删除地址结果
    """
    endpoint = f"customer/address/{address_id}"
    data = {
        "access_token": access_token
    }
    return client.make_request("DELETE", endpoint, data)
