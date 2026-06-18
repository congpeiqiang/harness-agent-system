---
name: fecmall-checkout
description: FecMall电商平台结账流程管理。提供结账页面初始化、地址选择、配送方式选择等功能。当用户需要完成订单结账流程时使用此skill。
---

# FecMall 结账流程

## 概述

本skill提供FecMall电商平台的结账流程管理，包括获取结账信息、选择地址、配送方式和更新订单信息等功能。

## 可用工具函数

```python
from app.mcp_server.fecmall_mcp.tools.onepage import (
    get_onepage_info,
    change_onepage_country,
    update_onepage_info
)
```

### 结账操作

```python
# 获取结账页面信息（需要登录）
get_onepage_info(client, access_token)

# 更改结账页面的国家（联动更新省/州列表）
change_onepage_country(client, access_token, country="US")

# 更新结账信息（地址、配送方式、支付方式）
address_data = {
    "shipping_address_id": "123",  # 收货地址ID
    "billing_address_id": "123",   # 账单地址ID
    "shipping_method": "flatrate_flatrate",  # 配送方式
    "payment_method": "check_money"  # 支付方式
}
update_onepage_info(client, access_token, address_data)
```

## 使用示例

### 初始化结账页面

```python
from app.mcp_server.fecmall_mcp.client import FecMallClient
from app.mcp_server.fecmall_mcp.config import FecMallConfig
from app.mcp_server.fecmall_mcp.tools.onepage import get_onepage_info

config = FecMallConfig()
client = FecMallClient(config)

# 获取结账页面信息
checkout_info = get_onepage_info(client, access_token="your_token")
```

### 更新结账信息

```python
from app.mcp_server.fecmall_mcp.tools.onepage import update_onepage_info

# 更新地址和配送/支付方式
checkout_data = {
    "shipping_address_id": "123",
    "billing_address_id": "123",
    "shipping_method": "flatrate_flatrate",
    "payment_method": "paypal_express"
}

result = update_onepage_info(client, access_token, checkout_data)
```

### 更改国家（联动省/州）

```python
from app.mcp_server.fecmall_mcp.tools.onepage import change_onepage_country

# 更改国家，获取该国家的省/州列表
result = change_onepage_country(client, access_token, country="CN")
```

## 结账页面数据结构

典型结账页面响应包含：

- **购物车信息**: 商品列表、金额小计
- **地址列表**: 用户保存的收货地址
- **配送方式**: 可用的配送选项及价格
- **支付方式**: 支持的支付方式列表

## 常见配送方式

- `flatrate_flatrate`: 固定运费
- `freeshipping_freeshipping`: 免运费

## 常见支付方式

- `check_money`: 支票/汇票
- `paypal_express`: PayPal快速结账
- `paypal_standard`: PayPal标准支付
- `alipay_standard`: 支付宝

## 结账流程

1. **获取结账信息**: 调用 `get_onepage_info` 加载结账页面
2. **选择地址**: 从用户的地址列表中选择收货地址
3. **配送方式**: 选择合适的配送方式
4. **支付方式**: 选择支付方式
5. **更新信息**: 调用 `update_onepage_info` 提交选择
6. **完成支付**: 根据支付方式跳转到相应支付页面

## 注意事项

1. **登录必需**: 结账流程需要access_token
2. **地址管理**: 如果没有地址，需要先调用 fecmall-address skill 添加地址
3. **联动更新**: 更改国家会影响省/州选项列表
