---
name: fecmall-review
description: FecMall电商平台评价管理。提供查看产品评价、添加产品评价、查看我的评价等功能。当用户需要查看产品评价、撰写评价、管理评价记录时使用此skill。
---

# FecMall 评价管理

## 概述

本skill提供FecMall电商平台的产品评价功能，包括查看产品评价、添加评价、查看用户的评价记录等。

## 可用工具函数

```python
from app.mcp_server.fecmall_mcp.tools.product_detail import (
    get_product_reviews,
    add_product_review
)
from app.mcp_server.fecmall_mcp.tools.customer_review import get_customer_reviews
```

### 评价操作

```python
# 获取产品的评价列表（无需登录）
get_product_reviews(client, product_id="123")

# 添加产品评价（需要登录且已购买）
add_product_review(
    client,
    access_token,
    product_id="123",
    star=5,
    summary="非常满意",
    review_content="产品质量很好，物流也快！",
    name="用户昵称"
)

# 获取当前用户的所有评价（需要登录）
get_customer_reviews(client, access_token)
```

## 使用示例

### 查看产品评价

```python
from app.mcp_server.fecmall_mcp.client import FecMallClient
from app.mcp_server.fecmall_mcp.config import FecMallConfig
from app.mcp_server.fecmall_mcp.tools.product_detail import get_product_reviews

config = FecMallConfig()
client = FecMallClient(config)

# 查看产品评价
reviews = get_product_reviews(client, product_id="123")
```

### 添加产品评价

```python
from app.mcp_server.fecmall_mcp.tools.product_detail import add_product_review

# 添加评价（需要购买过该产品）
result = add_product_review(
    client,
    access_token="your_token",
    product_id="123",
    star=5,  # 1-5星
    summary="五星好评",
    review_content="物超所值，下次还会购买！",
    name="Happy Customer"
)
```

### 查看我的评价

```python
from app.mcp_server.fecmall_mcp.tools.customer_review import get_customer_reviews

# 获取当前用户的所有评价
my_reviews = get_customer_reviews(client, access_token="your_token")
```

## 评分说明

- **star**: 1-5 的整数评分
  - 1星: 非常不满意
  - 2星: 不满意
  - 3星: 一般
  - 4星: 满意
  - 5星: 非常满意

## 注意事项

1. **查看评价**: 查看产品评价无需登录
2. **添加评价**: 
   - 需要登录（access_token）
   - 通常需要购买过该产品才能评价
3. **评价内容**: 
   - `summary`: 简短摘要（如"很好"、"不满意"）
   - `review_content`: 详细评价内容
   - `name`: 显示的评价人名称
