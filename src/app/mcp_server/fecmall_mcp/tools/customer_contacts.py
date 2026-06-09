"""
@File    :  customer_contacts.py
@Author  :  CongPeiQiang
@Time    :  2026/6/9
@Desc    :  联系表单API工具
"""
from typing import Dict, Any
from app.mcp_server.fecmall_mcp.client import FecMallClient


def get_contacts_info(client: FecMallClient) -> Dict[str, Any]:
    """
    获取联系表单页面信息
    Args:
        client: FecMall客户端实例
    Returns:
        Dict: 联系表单信息
    """
    endpoint = "customer/contact/index"
    return client.make_request("GET", endpoint, {})


def submit_contacts(
    client: FecMallClient,
    name: str,
    email: str,
    telephone: str,
    comment: str,
    captcha: str = ""
) -> Dict[str, Any]:
    """
    提交联系表单
    Args:
        client: FecMall客户端实例
        name: 姓名
        email: 邮箱
        telephone: 电话
        comment: 留言内容
        captcha: 验证码(可选)
    Returns:
        Dict: 提交结果
    """
    endpoint = "customer/contact/submit"
    data = {
        "name": name,
        "email": email,
        "telephone": telephone,
        "comment": comment
    }
    if captcha:
        data["captcha"] = captcha
    return client.make_request("POST", endpoint, data)
