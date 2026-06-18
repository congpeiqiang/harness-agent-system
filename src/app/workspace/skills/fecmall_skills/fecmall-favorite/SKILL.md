---
name: fecmall-favorite
description: FecMall电商平台收藏管理。提供查看收藏列表、添加收藏、移除收藏等功能。当用户需要管理产品收藏、查看收藏列表时使用此skill。
---

# FecMall 收藏管理

## 概述

本skill提供FecMall电商平台的产品收藏功能，包括查看收藏列表、添加收藏、移除收藏等。

## 可用工具函数

```python
from app.mcp_server.fecmall_mcp.tools.customer_favorite import (
    get_favorite_list,
    remove_favorite
)
from app.mcp_server.fecmall_mcp.tools.product_detail import add_to_favorite
```

### 收藏操作

```python
# 获取收藏列表（需要登录）
get_favorite_list(client, access_token)

# 添加产品到收藏（从产品详情页）
add_to_favorite(client, access_token, product_id="123")

# 从收藏列表中移除
remove_favorite(client, access_token, favorite_id="456")
```

## 使用示例

### 查看收藏列表

```python
from app.mcp_server.fecmall_mcp.client import FecMallClient
from app.mcp_server.fecmall_mcp.config import FecMallConfig
from app.mcp_server.fecmall_mcp.tools.customer_favorite import get_favorite_list

config = FecMallConfig()
client = FecMallClient(config)

favorites = get_favorite_list(client, access_token="your_token")
```

### 添加收藏

```python
from app.mcp_server.fecmall_mcp.tools.product_detail import add_to_favorite

# 浏览产品时添加到收藏
result = add_to_favorite(client, access_token, product_id="123")
```

### 移除收藏

```python
from app.mcp_server.fecmall_mcp.tools.customer_favorite import remove_favorite

# 从收藏列表移除
current_favorites = get_favorite_list(client, access_token)
# 找到要移除的favorite_id
result = remove_favorite(client, access_token, favorite_id="456")
```

## 字段说明

- **product_id**: 产品的唯一标识
- **favorite_id**: 收藏记录的唯一标识（用于移除收藏）

## 注意事项

1. **登录必需**: 所有收藏操作都需要access_token
2. **ID区别**: 
   - `product_id` 用于添加收藏
   - `favorite_id` 用于移除收藏（在收藏列表中返回）
3. **重复添加**: 同一产品重复添加收藏通常会返回已存在的提示
