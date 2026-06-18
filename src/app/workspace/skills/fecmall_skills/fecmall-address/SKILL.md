---
name: fecmall-address
description: FecMall电商平台地址管理。提供查看地址列表、添加地址、编辑地址、删除地址等功能。当用户需要管理收货地址、添加新地址、修改地址信息时使用此skill。
---

# FecMall 地址管理

## 概述

本skill提供FecMall电商平台的地址管理功能，包括查看地址列表、添加/编辑/删除地址等。

## 可用工具函数

```python
from app.mcp_server.fecmall_mcp.tools.address import (
    get_customer_addresses,
    get_address_info,
    change_address_country,
    save_customer_address,
    remove_customer_address
)
```

### 地址操作

```python
# 获取地址列表（需要登录）
get_customer_addresses(client, access_token)

# 获取单个地址详情（编辑时使用）
get_address_info(client, access_token, address_id="123")

# 更改国家（获取该国家的省/州列表）
change_address_country(client, access_token, country="US")

# 保存地址（添加新地址或更新已有地址）
address_data = {
    "address_id": "",  # 为空表示添加新地址，有值表示更新
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "telephone": "1234567890",
    "street1": "123 Main St",
    "street2": "Apt 4B",
    "city": "New York",
    "state": "NY",
    "country": "US",
    "zip": "10001",
    "is_default": "1"  # "1"表示设为默认地址
}
save_customer_address(client, access_token, address_data)

# 删除地址
remove_customer_address(client, access_token, address_id="123")
```

## 使用示例

### 查看地址列表

```python
from app.mcp_server.fecmall_mcp.client import FecMallClient
from app.mcp_server.fecmall_mcp.config import FecMallConfig
from app.mcp_server.fecmall_mcp.tools.address import get_customer_addresses

config = FecMallConfig()
client = FecMallClient(config)

addresses = get_customer_addresses(client, access_token="your_token")
```

### 添加新地址

```python
from app.mcp_server.fecmall_mcp.tools.address import save_customer_address

new_address = {
    "first_name": "张三",
    "last_name": "",
    "email": "zhangsan@example.com",
    "telephone": "13800138000",
    "street1": "北京市朝阳区xxx街道",
    "street2": "",
    "city": "北京市",
    "state": "北京市",
    "country": "CN",
    "zip": "100000",
    "is_default": "1"
}

result = save_customer_address(client, access_token, new_address)
```

### 编辑地址

```python
from app.mcp_server.fecmall_mcp.tools.address import get_address_info, save_customer_address

# 先获取地址详情
address_info = get_address_info(client, access_token, address_id="123")

# 修改后保存（带上address_id表示更新）
updated_address = {
    "address_id": "123",
    "first_name": "李四",
    "last_name": "",
    "email": "lisi@example.com",
    "telephone": "13900139000",
    "street1": "上海市浦东新区xxx路",
    "street2": "",
    "city": "上海市",
    "state": "上海市",
    "country": "CN",
    "zip": "200000",
    "is_default": "0"
}
result = save_customer_address(client, access_token, updated_address)
```

### 删除地址

```python
from app.mcp_server.fecmall_mcp.tools.address import remove_customer_address

result = remove_customer_address(client, access_token, address_id="123")
```

## 国家代码

常用国家代码：
- `CN`: 中国
- `US`: 美国
- `CA`: 加拿大
- `UK`: 英国
- `AU`: 澳大利亚
- `JP`: 日本

## 注意事项

1. **登录必需**: 所有地址操作都需要access_token
2. **字段完整性**: 保存地址时确保必填字段完整
3. **省/州联动**: 切换国家后，可能需要调用 `change_address_country` 获取新的省/州列表
4. **默认地址**: 设置 `is_default="1"` 可将该地址设为默认收货地址
