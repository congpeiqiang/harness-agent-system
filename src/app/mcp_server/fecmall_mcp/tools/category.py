"""
@File    :  category.py
@Author  :  CongPeiQiang
@Time    :  2026/6/9
@Desc    :  分类相关API工具
"""
from typing import Dict, Any
from app.mcp_server.fecmall_mcp.client import FecMallClient


def get_category_products(
    client: FecMallClient,
    category_id: str,
    sort_column: str = "",
    filter_attrs: Dict[str, Any] = None,
    filter_price: str = ""
) -> Dict[str, Any]:
    """
    获取分类下的产品列表
    Args:
        client: FecMall客户端实例
        category_id: 分类ID
        sort_column: 排序列
        filter_attrs: 属性筛选(JSON对象)
        filter_price: 价格筛选(如"20-30")
    Returns:
        Dict: 分类产品列表
    """
    endpoint = "catalog/category/product"
    data = {
        "categoryId": category_id
    }
    if sort_column:
        data["sortColumn"] = sort_column
    if filter_attrs:
        data["filterAttrs"] = filter_attrs
    if filter_price:
        data["filterPrice"] = filter_price
    return client.make_request("GET", endpoint, data)


def get_category_info(client: FecMallClient, category_id: str) -> Dict[str, Any]:
    """
    获取分类信息
    Args:
        client: FecMall客户端实例
        category_id: 分类ID
    Returns:
        Dict: 分类信息详情
    """
    endpoint = "catalog/category/index"
    data = {
        "categoryId": category_id
    }
    return client.make_request("GET", endpoint, data)
