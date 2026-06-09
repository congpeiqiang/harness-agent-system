"""
@File    :  order.py
@Author  :  CongPeiQiang
@Time    :  2026/6/8 21:05
@Desc    :  
"""
from typing import Dict, Any
from app.mcp_server.fecmall_mcp.client import FecMallClient

def init_customer_order(client: FecMallClient, access_token: str) -> Dict[str, Any]:
    """
    初始化客户订单
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
    Returns:
        Dict: 订单初始化结果
    """
    endpoint = "customer/order/index"
    data = {
        "access_token": access_token
    }
    return client.make_request("GET", endpoint, data)

def reorder_customer_order(client: FecMallClient, access_token: str, order_id: str) -> Dict[str, Any]:
    """
    重新订购
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
        order_id: 订单ID
    Returns:
        Dict: 重新订购结果
    """
    endpoint = "customer/order/reorder"
    data = {
        "access_token": access_token,
        "order_id": order_id
    }
    return client.make_request("GET", endpoint, data)

def view_customer_order(client: FecMallClient, access_token: str, order_id: str) -> Dict[str, Any]:
    """
    查看客户订单
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
        order_id: 订单ID
    Returns:
        Dict: 订单详情
    """
    endpoint = "customer/order/view"
    data = {
        "access_token": access_token,
        "order_id": order_id
    }
    return client.make_request("GET", endpoint, data)
