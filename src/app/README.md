# Harness Agent System

基于 LangGraph 和 MCP 的智能 Agent 系统。

## 目录结构

```
src/app/
├── main.py              # FastAPI 应用入口
├── api/                 # API 端点
├── agents/              # Agent 工厂
├── core/                # 配置和状态
├── middleware/           # 中间件
├── tools/               # 工具集合
├── schema/              # 请求/响应模型
├── processors/          # PDF 处理器
├── mcp_server/          # MCP 服务器
└── utils/               # 工具函数
```

## 开发

```bash
# 安装依赖
uv sync

# 启动开发服务器
make dev

# 运行测试
make test
```

## 文档

- [API 文档](../docs/api.md)
- [架构说明](../docs/architecture.md)
- [部署指南](../docs/deployment.md)
