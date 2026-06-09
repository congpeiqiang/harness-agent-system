"""
@File    :  auth.py
@Author  :  CongPeiQiang
@Time    :  2026/6/8 21:04
@Desc    :  
"""
from typing import Dict, Any
from app.mcp_server.fecmall_mcp.client import FecMallClient

def customer_login_submit(client: FecMallClient, email: str, password: str) -> Dict[str, Any]:
    """
    提交客户登录信息
    Args:
        client: FecMall客户端实例
        email: 客户邮箱
        password: 客户密码
    Returns:
        Dict: 登录响应结果
    """
    endpoint = "customer/login/account"
    data = {
        "email": email,
        "password": password
    }
    response = client.make_request("POST", endpoint, data, return_full=True)
    return response
    # return client.make_request("POST", endpoint, data)

def customer_login(client: FecMallClient, access_token: str) -> Dict[str, Any]:
    """
    验证客户登录状态
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
    Returns:
        Dict: 登录状态验证结果
    """
    endpoint = "customer/login"
    data = {
        "access_token": access_token
    }
    return client.make_request("POST", endpoint, data)
