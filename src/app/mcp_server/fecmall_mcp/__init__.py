"""
@File    :  __init__.py.py
@Author  :  CongPeiQiang
@Time    :  2026/6/8 20:46
@Desc    :  
"""
from app.mcp_server.fecmall_mcp.client import FecMallClient
from app.mcp_server.fecmall_mcp.config import FecMallConfig
from app.mcp_server.fecmall_mcp.tools.auth import customer_login_submit, customer_login
from app.mcp_server.fecmall_mcp.tools.address import (add_customer_address,
                                                      update_customer_address,
                                                      get_customer_addresses,
                                                      remove_customer_address
                                                      )
from app.mcp_server.fecmall_mcp.tools.order import init_customer_order,reorder_customer_order, view_customer_order
from app.mcp_server.fecmall_mcp.tools.product import search_products

__all__ = [
    "FecMallClient",
    "FecMallConfig",
    "customer_login_submit",
    "customer_login",
    "add_customer_address",
    "update_customer_address",
    "get_customer_addresses",
    "remove_customer_address",
    "init_customer_order",
    "reorder_customer_order",
    "view_customer_order",
    "search_products",
]