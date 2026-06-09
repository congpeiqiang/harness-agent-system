"""
@File    :  cart.py
@Author  :  CongPeiQiang
@Time    :  2026/6/9
@Desc    :  购物车相关API工具
"""
from typing import Dict, Any
from app.mcp_server.fecmall_mcp.client import FecMallClient


def get_cart(client: FecMallClient, access_token: str) -> Dict[str, Any]:
    """
    获取购物车信息
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
    Returns:
        Dict: 购物车信息
    """
    endpoint = "checkout/cart/index"
    data = {
        "access_token": access_token
    }
    return client.make_request("GET", endpoint, data)


def update_cart_item(
    client: FecMallClient,
    access_token: str,
    item_id: str,
    up_type: str
) -> Dict[str, Any]:
    """
    更新购物车项
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
        item_id: 购物车项ID
        up_type: 更新类型("less_one"/"add_one"/"remove")
    Returns:
        Dict: 更新结果
    """
    endpoint = "checkout/cart/updateinfo"
    data = {
        "access_token": access_token,
        "item_id": item_id,
        "up_type": up_type
    }
    return client.make_request("POST", endpoint, data)


def add_coupon(client: FecMallClient, access_token: str, coupon_code: str) -> Dict[str, Any]:
    """
    添加优惠券
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
        coupon_code: 优惠券代码
    Returns:
        Dict: 添加优惠券结果
    """
    endpoint = "checkout/cart/addcoupon"
    data = {
        "access_token": access_token,
        "coupon_code": coupon_code
    }
    return client.make_request("POST", endpoint, data)


def cancel_coupon(client: FecMallClient, access_token: str) -> Dict[str, Any]:
    """
    取消优惠券
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
    Returns:
        Dict: 取消优惠券结果
    """
    endpoint = "checkout/cart/cancelcoupon"
    data = {
        "access_token": access_token
    }
    return client.make_request("POST", endpoint, data)
