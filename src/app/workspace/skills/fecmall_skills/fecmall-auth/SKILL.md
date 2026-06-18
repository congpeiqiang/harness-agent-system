---
name: fecmall-auth
description: FecMall电商平台用户认证与注册管理。处理用户登录、注册、密码重置、忘记密码等认证流程。当用户需要登录账户、注册新账户、重置密码或找回密码时使用此skill。
---

# FecMall 认证管理

## 概述

本skill提供FecMall电商平台的完整用户认证流程，包括登录、注册、密码管理等功能。

## 可用工具函数

### 登录相关

```python
from app.mcp_server.fecmall_mcp.tools.auth import customer_login_submit, customer_login

# 用户登录
customer_login_submit(client, email, password)

# 验证登录状态
customer_login(client, access_token)
```

### 注册相关

```python
from app.mcp_server.fecmall_mcp.tools.customer_register import get_register_info, submit_register

# 获取注册页面信息（如验证码需求等）
get_register_info(client)

# 提交注册
submit_register(client, email, password, firstname, lastname, captcha="")
```

### 密码管理

```python
from app.mcp_server.fecmall_mcp.tools.customer_password import (
    forgot_password_init,
    forgot_password_send_code,
    reset_password_init,
    reset_password_submit
)

# 忘记密码流程
forgot_password_init(client)  # 初始化
code_result = forgot_password_send_code(client, email, captcha="")

# 重置密码流程
reset_password_init(client)
reset_password_submit(client, email, code, new_password, confirm_password)
```

### 联系表单（无需登录）

```python
from app.mcp_server.fecmall_mcp.tools.customer_contacts import get_contacts_info, submit_contacts

# 提交联系表单
submit_contacts(client, name, email, telephone, comment, captcha="")
```

## 使用示例

### 用户登录

```python
from app.mcp_server.fecmall_mcp.client import FecMallClient
from app.mcp_server.fecmall_mcp.config import FecMallConfig
from app.mcp_server.fecmall_mcp.tools.auth import customer_login_submit

config = FecMallConfig()
client = FecMallClient(config)

# 登录获取access_token
result = customer_login_submit(client, "user@example.com", "password123")
# 从响应中获取 access_token
```

### 用户注册

```python
from app.mcp_server.fecmall_mcp.tools.customer_register import submit_register

result = submit_register(
    client,
    email="newuser@example.com",
    password="password123",
    firstname="John",
    lastname="Doe"
)
```

### 忘记密码

```python
from app.mcp_server.fecmall_mcp.tools.customer_password import forgot_password_send_code, reset_password_submit

# 发送验证码
forgot_password_send_code(client, email="user@example.com")

# 使用验证码重置密码
reset_password_submit(
    client,
    email="user@example.com",
    code="123456",
    new_password="newpass123",
    confirm_password="newpass123"
)
```

## 注意事项

1. **access_token处理**: 登录成功后，从响应中获取 `Access-Token`，后续需要登录的接口都需要此token
2. **验证码**: 某些操作可能需要验证码，先调用 `get_register_info` 或 `forgot_password_init` 检查是否需要
3. **错误处理**: API调用可能失败，需要处理异常情况
