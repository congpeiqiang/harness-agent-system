"""
@File    :  customer_favorite.py
@Author  :  CongPeiQiang
@Time    :  2026/6/9
@Desc    :  收藏管理API工具
"""
from typing import Dict, Any
from app.mcp_server.fecmall_mcp.client import FecMallClient


def get_favorite_list(client: FecMallClient, access_token: str) -> Dict[str, Any]:
    """
    获取收藏列表
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
    Returns:
        Dict: 收藏列表
    """
    endpoint = "customer/productfavorite/index"
    data = {
        "access_token": access_token
    }
    return client.make_request("GET", endpoint, data)


def remove_favorite(
    client: FecMallClient,
    access_token: str,
    favorite_id: str
) -> Dict[str, Any]:
    """
    移除收藏
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
        favorite_id: 收藏ID
    Returns:
        Dict: 移除结果
    """
    endpoint = "customer/productfavorite/remove"
    data = {
        "access_token": access_token,
        "favorite_id": favorite_id
    }
    return client.make_request("POST", endpoint, data)
