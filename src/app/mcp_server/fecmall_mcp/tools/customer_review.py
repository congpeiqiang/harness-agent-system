"""
@File    :  customer_review.py
@Author  :  CongPeiQiang
@Time    :  2026/6/9
@Desc    :  评价管理API工具
"""
from typing import Dict, Any
from app.mcp_server.fecmall_mcp.client import FecMallClient


def get_customer_reviews(client: FecMallClient, access_token: str) -> Dict[str, Any]:
    """
    获取客户的所有评价
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
    Returns:
        Dict: 客户评价列表
    """
    endpoint = "customer/productreview/index"
    data = {
        "access_token": access_token
    }
    return client.make_request("GET", endpoint, data)
