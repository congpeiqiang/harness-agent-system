"""
@File    :  order.py
@Author  :  CongPeiQiang
@Time    :  2026/6/8 21:05
@Desc    :  
"""
from typing import Dict, Any
from app.mcp_server.fecmall_mcp.client import FecMallClient

def init_customer_order(client: FecMallClient, access_token: str, cart_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    初始化客户订单
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
        cart_data: 购物车数据
    Returns:
        Dict: 订单初始化结果
    """
    endpoint = "customer/order/init"
    data = {
        "access_token": access_token,
        **cart_data
    }
    return client.make_request("POST", endpoint, data)

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
    endpoint = f"customer/order/reorder/{order_id}"
    data = {
        "access_token": access_token
    }
    return client.make_request("POST", endpoint, data)

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
    endpoint = f"customer/order/view/{order_id}"
    data = {
        "access_token": access_token
    }
    return client.make_request("GET", endpoint, data)
