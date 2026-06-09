"""
@File    :  customer_account.py
@Author  :  CongPeiQiang
@Time    :  2026/6/9
@Desc    :  客户账户API工具
"""
from typing import Dict, Any
from app.mcp_server.fecmall_mcp.client import FecMallClient


def get_customer_info(client: FecMallClient, access_token: str) -> Dict[str, Any]:
    """
    获取客户信息
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
    Returns:
        Dict: 客户信息
    """
    endpoint = "customer/account/index"
    data = {
        "access_token": access_token
    }
    return client.make_request("GET", endpoint, data)


def get_account_edit(client: FecMallClient, access_token: str) -> Dict[str, Any]:
    """
    获取账户编辑页面信息
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
    Returns:
        Dict: 账户编辑信息
    """
    endpoint = "customer/editaccount/index"
    data = {
        "access_token": access_token
    }
    return client.make_request("GET", endpoint, data)


def submit_account_edit(
    client: FecMallClient,
    access_token: str,
    firstname: str,
    lastname: str,
    current_password: str = "",
    new_password: str = ""
) -> Dict[str, Any]:
    """
    提交账户编辑信息
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
        firstname: 名字
        lastname: 姓氏
        current_password: 当前密码(可选)
        new_password: 新密码(可选)
    Returns:
        Dict: 编辑结果
    """
    endpoint = "customer/editaccount/update"
    data = {
        "access_token": access_token,
        "firstname": firstname,
        "lastname": lastname
    }
    if current_password:
        data["current_password"] = current_password
    if new_password:
        data["new_password"] = new_password
    return client.make_request("POST", endpoint, data)
