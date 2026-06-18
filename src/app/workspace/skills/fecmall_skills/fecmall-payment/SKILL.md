---
name: fecmall-payment
description: FecMall电商平台支付处理。支持PayPal、支付宝、支票/汇票等多种支付方式。当用户需要完成订单支付、选择支付方式、查看支付状态时使
用此skill。
---

# FecMall 支付管理

## 概述

本skill提供FecMall电商平台的支付功能，支持PayPal（快速结账/标准支付）、支付宝、支票/汇票等多种支付方式。

## 可用工具函数

```python
from app.mcp_server.fecmall_mcp.tools.payment import (
    paypal_express_start,
    paypal_express_review,
    paypal_express_submit,
    paypal_standard_start,
    paypal_standard_review,
    alipay_standard_start,
    alipay_standard_review,
    checkmoney_start,
    payment_success
)
```

### PayPal 快速结账

```python
# 启动PayPal快速结账
paypal_express_start(client, access_token)

# 查看PayPal订单预览
paypal_express_review(client, access_token)

# 提交PayPal订单
paypal_express_submit(client, access_token, order_data={})
```

### PayPal 标准支付

```python
# 启动PayPal标准支付
paypal_standard_start(client, access_token)

# 查看订单预览
paypal_standard_review(client, access_token)
```

### 支付宝标准支付

```python
# 启动支付宝支付
alipay_standard_start(client, access_token)

# 查看订单预览
alipay_standard_review(client, access_token)
```

### 支票/汇票支付

```python
# 启动支票支付
checkmoney_start(client, access_token)
```

### 支付成功回调

```python
# 支付成功后调用
payment_success(client, access_token)
```

## 使用示例

### PayPal 快速结账流程

```python
from app.mcp_server.fecmall_mcp.client import FecMallClient
from app.mcp_server.fecmall_mcp.config import FecMallConfig
from app.mcp_server.fecmall_mcp.tools.payment import (
    paypal_express_start,
    paypal_express_review,
    paypal_express_submit
)

config = FecMallConfig()
client = FecMallClient(config)
access_token = "your_token"

# 1. 启动PayPal支付
start_result = paypal_express_start(client, access_token)

# 2. 用户完成PayPal授权后，查看订单预览
review_result = paypal_express_review(client, access_token)

# 3. 提交订单完成支付
order_data = {
    # 根据实际需要的订单数据填写
}
submit_result = paypal_express_submit(client, access_token, order_data)
```

### 支付宝支付

```python
from app.mcp_server.fecmall_mcp.tools.payment import alipay_standard_start, alipay_standard_review

# 启动支付宝支付
alipay_result = alipay_standard_start(client, access_token)

# 查看订单预览
review_result = alipay_standard_review(client, access_token)
```

## 支付流程说明

### PayPal Express 流程

1. **start**: 获取PayPal跳转URL
2. 用户跳转至PayPal完成授权
3. **review**: 查看订单详情和金额
4. **submit**: 确认并提交订单

### 支付宝流程

1. **start**: 获取支付宝支付参数/二维码
2. 用户完成支付宝扫码支付
3. **review**: 确认支付状态

## 注意事项

1. **登录必需**: 所有支付操作都需要access_token
2. **前置条件**: 支付前需要完成结账流程（选择地址、配送方式等）
3. **回调处理**: 实际支付完成后，需要处理支付网关的回调通知
4. **订单数据**: `paypal_express_submit` 需要传入完整的订单数据
