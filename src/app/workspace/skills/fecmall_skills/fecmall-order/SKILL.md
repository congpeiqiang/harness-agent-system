---
name: fecmall-order
description: FecMall电商平台订单管理。提供查看订单列表、订单详情、重新下单等功能。当用户需要查看历史订单、跟踪订单状态、重新购买时使用此skill。
---

# FecMall 订单管理

## 概述

本skill提供FecMall电商平台的订单管理功能，包括查看订单列表、订单详情、重新下单等。

## 可用工具函数

```python
from app.mcp_server.fecmall_mcp.tools.order import (
    init_customer_order,
    reorder_customer_order,
    view_customer_order
)
```

### 订单操作

```python
# 初始化订单页面，获取订单列表（需要登录）
init_customer_order(client, access_token)

# 查看订单详情
view_customer_order(client, access_token, order_id="12345")

# 重新下单（将订单中的商品重新加入购物车）
reorder_customer_order(client, access_token, order_id="12345")
```

## 使用示例

### 查看订单列表

```python
from app.mcp_server.fecmall_mcp.client import FecMallClient
from app.mcp_server.fecmall_mcp.config import FecMallConfig
from app.mcp_server.fecmall_mcp.tools.order import init_customer_order

config = FecMallConfig()
client = FecMallClient(config)

orders = init_customer_order(client, access_token="your_token")
```

### 查看订单详情

```python
from app.mcp_server.fecmall_mcp.tools.order import view_customer_order

order_detail = view_customer_order(
    client,
    access_token="your_token",
    order_id="ORDER-2024-001"
)
```

### 重新下单

```python
from app.mcp_server.fecmall_mcp.tools.order import reorder_customer_order

# 将历史订单的商品重新加入购物车
result = reorder_customer_order(
    client,
    access_token="your_token",
    order_id="ORDER-2024-001"
)
```

## 订单状态说明

常见订单状态：
- `pending`: 待处理
- `processing`: 处理中
- `complete`: 已完成
- `cancelled`: 已取消
- `holded`: 已暂停

## 注意事项

1. **登录必需**: 所有订单操作都需要access_token
2. **订单ID格式**: 订单ID通常由系统生成，如 "ORDER-2024-001"
3. **重新下单**: 重新下单只是将商品加入购物车，需要后续完成结账流程
