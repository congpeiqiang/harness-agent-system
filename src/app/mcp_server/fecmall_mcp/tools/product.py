"""
@File    :  product.py
@Author  :  CongPeiQiang
@Time    :  2026/6/8 21:05
@Desc    :  
"""
from typing import Dict, Any
from app.mcp_server.fecmall_mcp.client import FecMallClient

def search_products(client: FecMallClient, search_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    搜索产品
    Args:
        client: FecMall客户端实例
        search_params: 搜索参数字典
    Returns:
        Dict: 搜索结果
    """
    endpoint = "product/search"
    return client.make_request("GET", endpoint, search_params)
