"""
@File    :  product_detail.py
@Author  :  CongPeiQiang
@Time    :  2026/6/9
@Desc    :  产品详情API工具
"""
from typing import Dict, Any
from app.mcp_server.fecmall_mcp.client import FecMallClient


def get_product_info(client: FecMallClient, product_id: str) -> Dict[str, Any]:
    """
    获取产品详情信息
    Args:
        client: FecMall客户端实例
        product_id: 产品ID
    Returns:
        Dict: 产品详情
    """
    endpoint = "catalog/product/index"
    data = {
        "product_id": product_id
    }
    return client.make_request("GET", endpoint, data)


def add_to_cart_from_product(
    client: FecMallClient,
    access_token: str,
    product_id: str,
    qty: int,
    custom_option: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    从产品页面添加到购物车
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
        product_id: 产品ID
        qty: 数量
        custom_option: 自定义选项
    Returns:
        Dict: 添加结果
    """
    endpoint = "checkout/cart/add"
    data = {
        "access_token": access_token,
        "product_id": product_id,
        "qty": qty
    }
    if custom_option:
        data["custom_option"] = custom_option
    return client.make_request("POST", endpoint, data)


def add_to_favorite(
    client: FecMallClient,
    access_token: str,
    product_id: str
) -> Dict[str, Any]:
    """
    添加产品到收藏
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
        product_id: 产品ID
    Returns:
        Dict: 添加结果
    """
    endpoint = "catalog/product/favorite"
    data = {
        "access_token": access_token,
        "product_id": product_id
    }
    return client.make_request("POST", endpoint, data)


def get_product_reviews(client: FecMallClient, product_id: str) -> Dict[str, Any]:
    """
    获取产品评价列表
    Args:
        client: FecMall客户端实例
        product_id: 产品ID
    Returns:
        Dict: 产品评价列表
    """
    endpoint = "catalog/reviewproduct/lists"
    data = {
        "product_id": product_id
    }
    return client.make_request("GET", endpoint, data)


def add_product_review(
    client: FecMallClient,
    access_token: str,
    product_id: str,
    star: int,
    summary: str,
    review_content: str,
    name: str
) -> Dict[str, Any]:
    """
    添加产品评价
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
        product_id: 产品ID
        star: 评分(1-5)
        summary: 评价摘要
        review_content: 评价内容
        name: 评价人姓名
    Returns:
        Dict: 添加结果
    """
    endpoint = "catalog/reviewproduct/add"
    data = {
        "access_token": access_token,
        "product_id": product_id,
        "star": star,
        "summary": summary,
        "review_content": review_content,
        "name": name
    }
    return client.make_request("POST", endpoint, data)
