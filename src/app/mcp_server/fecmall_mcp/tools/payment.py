"""
@File    :  payment.py
@Author  :  CongPeiQiang
@Time    :  2026/6/9
@Desc    :  支付相关API工具
"""
from typing import Dict, Any
from app.mcp_server.fecmall_mcp.client import FecMallClient


def paypal_express_start(client: FecMallClient, access_token: str) -> Dict[str, Any]:
    """
    启动PayPal快速结账
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
    Returns:
        Dict: 支付启动结果
    """
    endpoint = "payment/paypal/express/start"
    data = {
        "access_token": access_token
    }
    return client.make_request("POST", endpoint, data)


def paypal_express_review(client: FecMallClient, access_token: str) -> Dict[str, Any]:
    """
    查看PayPal快速结账订单
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
    Returns:
        Dict: 订单预览信息
    """
    endpoint = "payment/paypal/express/review"
    data = {
        "access_token": access_token
    }
    return client.make_request("GET", endpoint, data)


def paypal_express_submit(
    client: FecMallClient,
    access_token: str,
    order_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    提交PayPal快速结账订单
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
        order_data: 订单数据
    Returns:
        Dict: 订单提交结果
    """
    endpoint = "payment/paypal/express/submitorder"
    data = {
        "access_token": access_token,
        **order_data
    }
    return client.make_request("POST", endpoint, data)


def paypal_standard_start(client: FecMallClient, access_token: str) -> Dict[str, Any]:
    """
    启动PayPal标准支付
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
    Returns:
        Dict: 支付启动结果
    """
    endpoint = "payment/paypal/standard/start"
    data = {
        "access_token": access_token
    }
    return client.make_request("POST", endpoint, data)


def paypal_standard_review(client: FecMallClient, access_token: str) -> Dict[str, Any]:
    """
    查看PayPal标准支付订单
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
    Returns:
        Dict: 订单预览信息
    """
    endpoint = "payment/paypal/standard/review"
    data = {
        "access_token": access_token
    }
    return client.make_request("GET", endpoint, data)


def alipay_standard_start(client: FecMallClient, access_token: str) -> Dict[str, Any]:
    """
    启动支付宝标准支付
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
    Returns:
        Dict: 支付启动结果
    """
    endpoint = "payment/alipay/standard/start"
    data = {
        "access_token": access_token
    }
    return client.make_request("POST", endpoint, data)


def alipay_standard_review(client: FecMallClient, access_token: str) -> Dict[str, Any]:
    """
    查看支付宝标准支付订单
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
    Returns:
        Dict: 订单预览信息
    """
    endpoint = "payment/alipay/standard/review"
    data = {
        "access_token": access_token
    }
    return client.make_request("GET", endpoint, data)


def checkmoney_start(client: FecMallClient, access_token: str) -> Dict[str, Any]:
    """
    启动支票/汇票支付
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
    Returns:
        Dict: 支付启动结果
    """
    endpoint = "payment/checkmoney/start"
    data = {
        "access_token": access_token
    }
    return client.make_request("POST", endpoint, data)


def payment_success(client: FecMallClient, access_token: str) -> Dict[str, Any]:
    """
    支付成功回调
    Args:
        client: FecMall客户端实例
        access_token: 访问令牌
    Returns:
        Dict: 支付成功处理结果
    """
    endpoint = "payment/success"
    data = {
        "access_token": access_token
    }
    return client.make_request("POST", endpoint, data)
