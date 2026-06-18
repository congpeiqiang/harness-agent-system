---
name: fecmall-product
description: FecMall电商平台产品浏览与搜索。提供产品搜索、分类浏览、产品详情查看等功能。当用户需要搜索产品、查看产品详情、浏览分类产品时使用此skill。
---

# FecMall 产品管理

## 概述

本skill提供FecMall电商平台的产品相关功能，包括产品搜索、分类浏览、产品详情查看、收藏和评价等功能。

## 可用工具函数

### 产品搜索

```python
from app.mcp_server.fecmall_mcp.tools.product import search_products

# 搜索产品
search_products(client, search_params={"q": "关键词"})
```

### 产品详情

```python
from app.mcp_server.fecmall_mcp.tools.product_detail import (
    get_product_info,
    add_to_cart_from_product,
    add_to_favorite,
    get_product_reviews,
    add_product_review
)

# 获取产品详情
get_product_info(client, product_id="123")

# 从产品页面添加到购物车（需要登录）
add_to_cart_from_product(client, access_token, product_id, qty=1, custom_option=None)

# 添加产品到收藏（需要登录）
add_to_favorite(client, access_token, product_id)

# 获取产品评价
get_product_reviews(client, product_id)

# 添加产品评价（需要登录）
add_product_review(client, access_token, product_id, star=5, summary="很好", review_content="产品质量不错", name="用户")
```

### 分类浏览

```python
from app.mcp_server.fecmall_mcp.tools.category import get_category_products, get_category_info

# 获取分类信息
get_category_info(client, category_id="456")

# 获取分类下产品列表
get_category_products(
    client,
    category_id="456",
    sort_column="price",  # 可选：排序字段
    filter_attrs={"color": "red"},  # 可选：属性筛选
    filter_price="20-50"  # 可选：价格区间
)
```

## 使用示例

### 搜索产品

```python
from app.mcp_server.fecmall_mcp.client import FecMallClient
from app.mcp_server.fecmall_mcp.config import FecMallConfig
from app.mcp_server.fecmall_mcp.tools.product import search_products

config = FecMallConfig()
client = FecMallClient(config)

# 搜索关键词
result = search_products(client, {"q": "iPhone"})
```

### 查看产品详情并加入购物车

```python
from app.mcp_server.fecmall_mcp.tools.product_detail import get_product_info, add_to_cart_from_product

# 获取产品详情
product = get_product_info(client, product_id="123")

# 添加到购物车（需要先登录获取access_token）
result = add_to_cart_from_product(
    client,
    access_token="your_token",
    product_id="123",
    qty=2,
    custom_option={"color": "black"}
)
```

### 浏览分类产品

```python
from app.mcp_server.fecmall_mcp.tools.category import get_category_products

# 获取分类产品，带筛选条件
products = get_category_products(
    client,
    category_id="10",
    sort_column="price",
    filter_price="100-500"
)
```

## 注意事项

1. **产品ID获取**: 通过搜索或分类浏览获取产品ID，再用ID查询详情
2. **自定义选项**: 某些产品有自定义选项（颜色、尺寸等），添加到购物车时需指定
3. **登录要求**: 收藏、评价、加购等功能需要用户登录（需要access_token）
