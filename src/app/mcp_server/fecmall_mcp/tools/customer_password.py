"""
@File    :  customer_password.py
@Author  :  CongPeiQiang
@Time    :  2026/6/9
@Desc    :  密码管理API工具
"""
from typing import Dict, Any
from app.mcp_server.fecmall_mcp.client import FecMallClient


def forgot_password_init(client: FecMallClient) -> Dict[str, Any]:
    """
    初始化忘记密码流程
    Args:
        client: FecMall客户端实例
    Returns:
        Dict: 初始化信息
    """
    endpoint = "customer/forgot/password"
    return client.make_request("GET", endpoint, {})


def forgot_password_send_code(
    client: FecMallClient,
    email: str,
    captcha: str = ""
) -> Dict[str, Any]:
    """
    发送忘记密码验证码
    Args:
        client: FecMall客户端实例
        email: 邮箱
        captcha: 验证码(可选)
    Returns:
        Dict: 发送结果
    """
    endpoint = "customer/forgot/sendcode"
    data = {
        "email": email
    }
    if captcha:
        data["captcha"] = captcha
    return client.make_request("POST", endpoint, data)


def reset_password_init(client: FecMallClient) -> Dict[str, Any]:
    """
    初始化密码重置流程
    Args:
        client: FecMall客户端实例
    Returns:
        Dict: 初始化信息
    """
    endpoint = "customer/forgot/resetpassword"
    return client.make_request("GET", endpoint, {})


def reset_password_submit(
    client: FecMallClient,
    email: str,
    code: str,
    new_password: str,
    confirm_password: str
) -> Dict[str, Any]:
    """
    提交密码重置
    Args:
        client: FecMall客户端实例
        email: 邮箱
        code: 验证码
        new_password: 新密码
        confirm_password: 确认新密码
    Returns:
        Dict: 重置结果
    """
    endpoint = "customer/forgot/submitresetpassword"
    data = {
        "email": email,
        "code": code,
        "new_password": new_password,
        "confirm_password": confirm_password
    }
    return client.make_request("POST", endpoint, data)
