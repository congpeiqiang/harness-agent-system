# API 文档

## 基础 URL

```
http://localhost:2026
```

## 认证

除 `/health` 和 `/ok` 外，所有 API 端点均需通过 `X-API-Key` 请求头提供 API 密钥：

```bash
curl -H "X-API-Key: your-api-key" http://localhost:2026/invoke
```

## 端点说明

### POST /invoke

同步调用 Agent。请求在线程池中处理。

**请求体：**

```json
{
  "messages": [
    {"role": "user", "content": "北京今天天气怎么样？"}
  ],
  "config": {
    "configurable": {
      "thread_id": "thread-123"
    }
  },
  "context": {
    "user_id": "user-456",
    "thread_id": "thread-123"
  }
}
```

**响应：**

```json
{
  "messages": [
    {"role": "user", "content": "北京今天天气怎么样？"},
    {"role": "assistant", "content": "北京今天天气晴朗..."}
  ]
}
```

### POST /ainvoke

异步调用 Agent。请求格式与 `/invoke` 相同。

**请求/响应：** 与 `/invoke` 相同。

### POST /stream

同步流式响应，通过服务器发送事件 (SSE) 返回。

**请求体：** 与 `/invoke` 相同。

**响应：** `text/event-stream`

```
data: {"messages": [...]}

data: {"messages": [...], "tools": [...]}

data: [DONE]
```

### POST /astream

异步流式响应，通过 SSE 返回。

**请求/响应：** 与 `/stream` 相同。

### GET /health

健康检查端点，用于容器编排。

**响应：**

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime_seconds": 123.45
}
```

### GET /ok

简单存活探针。

**响应：**

```json
{
  "status": "ok"
}
```

### GET /metrics

基础指标端点。

**响应：**

```json
{
  "uptime_seconds": 123.45,
  "version": "0.1.0"
}
```

## 交互式文档

- **Swagger UI**: http://localhost:2026/docs
- **ReDoc**: http://localhost:2026/redoc

## 错误响应

### 403 禁止访问

```json
{
  "detail": "无效的 API Key"
}
```

### 429 请求过多

```json
{
  "detail": "超过速率限制：每分钟 60 次"
}
```

### 500 服务器内部错误

```json
{
  "detail": "Agent 执行失败"
}
```
