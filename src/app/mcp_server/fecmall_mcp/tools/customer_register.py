"""
@File    :  customer_register.py
@Author  :  CongPeiQiang
@Time    :  2026/6/9
@Desc    :  客户注册API工具
"""
from typing import Dict, Any
from app.mcp_server.fecmall_mcp.client import FecMallClient


def get_register_info(client: FecMallClient) -> Dict[str, Any]:
    """
    获取注册页面信息
    Args:
        client: FecMall客户端实例
    Returns:
        Dict: 注册页面信息
    """
    endpoint = "customer/register/index"
    return client.make_request("GET", endpoint, {})


def submit_register(
    client: FecMallClient,
    email: str,
    password: str,
    firstname: str,
    lastname: str,
    captcha: str = ""
) -> Dict[str, Any]:
    """
    提交客户注册信息
    Args:
        client: FecMall客户端实例
        email: 邮箱
        password: 密码
        firstname: 名字
        lastname: 姓氏
        captcha: 验证码(可选)
    Returns:
        Dict: 注册结果
    """
    endpoint = "customer/register/account"
    data = {
        "email": email,
        "password": password,
        "firstname": firstname,
        "lastname": lastname
    }
    if captcha:
        data["captcha"] = captcha
    return client.make_request("POST", endpoint, data)
