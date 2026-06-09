"""
@File    :  server.py
@Author  :  CongPeiQiang
@Time    :  2026/6/8 21:07
@Desc    :  
"""
from fastmcp import FastMCP
from typing import Dict, Any
import json
from app.mcp_server.fecmall_mcp import (
    FecMallConfig,
    FecMallClient,
    customer_login_submit,
    customer_login,
    add_customer_address,
    update_customer_address,
    get_customer_addresses,
    remove_customer_address,
    init_customer_order,
    reorder_customer_order,
    view_customer_order,
    search_products
)

# 创建FastMCP实例
mcp = FastMCP("FecMall MCP Server")

# 初始化配置和客户端
config = FecMallConfig()
print(f"config: {config}")
client = FecMallClient(config)

@mcp.tool()
def customer_login_submit_tool(email: str, password: str) -> str:
    """
    提交客户登录信息
    Args:
        email: 客户邮箱
        password: 客户密码
    Returns:
        str: 登录响应结果
    """
    try:
        print(f"customer_login_submit_tool-1: {client}, {email}, {password}")
        result = customer_login_submit(client, email, password)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

@mcp.tool()
def customer_login_tool(access_token: str) -> str:
    """
    验证客户登录状态
    Args:
        access_token: 访问令牌
    Returns:
        str: 登录状态验证结果
    """
    try:
        result = customer_login(client, access_token)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

@mcp.tool()
def add_customer_address_tool(access_token: str, address_data: Dict[str, Any]) -> str:
    """
    添加客户地址
    Args:
        access_token: 访问令牌
        address_data: 地址信息字典
    Returns:
        str: 添加地址结果
    """
    try:
        result = add_customer_address(client, access_token, address_data)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

@mcp.tool()
def update_customer_address_tool(access_token: str, address_id: str, address_data: Dict[str, Any]) -> str:
    """
    更新客户地址
    Args:
        access_token: 访问令牌
        address_id: 地址ID
        address_data: 地址信息字典
    Returns:
        str: 更新地址结果
    """
    try:
        result = update_customer_address(client, access_token, address_id, address_data)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

@mcp.tool()
def get_customer_addresses_tool(access_token: str) -> str:
    """
    获取客户地址列表
    Args:
        access_token: 访问令牌
    Returns:
        str: 地址列表
    """
    try:
        result = get_customer_addresses(client, access_token)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

@mcp.tool()
def remove_customer_address_tool(access_token: str, address_id: str) -> str:
    """
    删除客户地址
    Args:
        access_token: 访问令牌
        address_id: 地址ID
    Returns:
        str: 删除地址结果
    """
    try:
        result = remove_customer_address(client, access_token, address_id)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

@mcp.tool()
def init_customer_order_tool(access_token: str, cart_data: Dict[str, Any]) -> str:
    """
    初始化客户订单
    Args:
        access_token: 访问令牌
        cart_data: 购物车数据
    Returns:
        str: 订单初始化结果
    """
    try:
        result = init_customer_order(client, access_token, cart_data)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

@mcp.tool()
def reorder_customer_order_tool(access_token: str, order_id: str) -> str:
    """
    重新订购
    Args:
        access_token: 访问令牌
        order_id: 订单ID
    Returns:
        str: 重新订购结果
    """
    try:
        result = reorder_customer_order(client, access_token, order_id)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

@mcp.tool()
def view_customer_order_tool(access_token: str, order_id: str) -> str:
    """
    查看客户订单
    Args:
        access_token: 访问令牌
        order_id: 订单ID
    Returns:
        str: 订单详情
    """
    try:
        result = view_customer_order(client, access_token, order_id)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

@mcp.tool()
def search_products_tool(search_params: Dict[str, Any]) -> str:
    """
    搜索产品
    Args:
        search_params: 搜索参数字典
    Returns:
        str: 搜索结果
    """
    try:
        result = search_products(client, search_params)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

if __name__ == "__main__":
    mcp.run(transport="sse", port=8000, host="0.0.0.0")
