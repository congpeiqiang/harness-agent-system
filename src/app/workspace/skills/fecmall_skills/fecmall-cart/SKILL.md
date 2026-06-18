---
name: fecmall-cart
description: FecMall电商平台购物车管理。提供查看购物车、更新商品数量、添加优惠券等功能。当用户需要管理购物车内容、修改商品数量、使用优惠券时使用此skill。
---

# FecMall 购物车管理

## 概述

本skill提供FecMall电商平台的购物车管理功能，包括查看购物车、更新商品数量、添加/取消优惠券等。

## 可用工具函数

```python
from app.mcp_server.fecmall_mcp.tools.cart import (
    get_cart,
    update_cart_item,
    add_coupon,
    cancel_coupon
)
from app.mcp_server.fecmall_mcp.tools.product_detail import add_to_cart_from_product
```

### 购物车操作

```python
# 获取购物车信息（需要登录）
get_cart(client, access_token)

# 更新购物车项
# up_type支持: "less_one"(减1), "add_one"(加1), "remove"(移除)
update_cart_item(client, access_token, item_id="123", up_type="add_one")

# 添加优惠券
add_coupon(client, access_token, coupon_code="SAVE10")

# 取消优惠券
cancel_coupon(client, access_token)
```

### 从产品页添加

```python
from app.mcp_server.fecmall_mcp.tools.product_detail import add_to_cart_from_product

# 从产品详情页添加到购物车
add_to_cart_from_product(
    client,
    access_token,
    product_id="123",
    qty=1,
    custom_option=None
)
```

## 使用示例

### 查看购物车

```python
from app.mcp_server.fecmall_mcp.client import FecMallClient
from app.mcp_server.fecmall_mcp.config import FecMallConfig
from app.mcp_server.fecmall_mcp.tools.cart import get_cart

config = FecMallConfig()
client = FecMallClient(config)

cart_info = get_cart(client, access_token="your_token")
```

### 修改购物车商品数量

```python
from app.mcp_server.fecmall_mcp.tools.cart import update_cart_item

# 增加数量
update_cart_item(client, access_token, item_id="1001", up_type="add_one")

# 减少数量
update_cart_item(client, access_token, item_id="1001", up_type="less_one")

# 移除商品
update_cart_item(client, access_token, item_id="1001", up_type="remove")
```

### 使用优惠券

```python
from app.mcp_server.fecmall_mcp.tools.cart import add_coupon, cancel_coupon

# 添加优惠券
add_coupon(client, access_token, coupon_code="DISCOUNT20")

# 取消优惠券
cancel_coupon(client, access_token)
```

## 购物车数据结构

典型购物车响应包含：
- 商品列表（item_id, product_id, name, qty, price等）
- 小计金额
- 优惠券信息
- 总计金额

## 注意事项

1. **登录必需**: 所有购物车操作都需要access_token
2. **item_id vs product_id**: 
   - `product_id` 是商品的唯一标识
   - `item_id` 是购物车项的标识，用于更新数量
3. **优惠券**: 先添加优惠券再结算，优惠券可能有使用条件（如最低消费金额）
