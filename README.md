# Harness Agent System

基于 LangGraph 和 MCP（模型上下文协议）的智能 Agent 系统，面向生产级 AI Agent 部署设计。

## 项目概述

本系统提供完整的 Agent 基础设施，包括：
- **LangGraph Agent**：支持多轮对话、工具调用、中间件链的智能代理
- **MCP 集成**：通过模型上下文协议连接外部工具和数据源
- **FastAPI 服务**：高性能异步 API 服务，支持 SSE 流式响应
- **多模型支持**：DeepSeek、豆包视觉模型等
- **PDF 解析**：PyMuPDF4LLM + Docling 多模态解析

## 快速开始

### 环境要求
- Python 3.13.5
- uv 包管理器（推荐）

### 安装

```bash
# 克隆项目
git clone https://github.com/your-org/harness-agent-system.git
cd harness-agent-system

# 安装依赖
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥
```

### 启动服务

```bash
# 使用 Make
make dev

# 或直接运行
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 2026
```

服务启动后访问 http://localhost:2026/docs 查看 API 文档。

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/invoke` | POST | 同步调用 Agent |
| `/ainvoke` | POST | 异步调用 Agent |
| `/stream` | POST | 同步流式响应（SSE） |
| `/astream` | POST | 异步流式响应（SSE） |
| `/health` | GET | 健康检查 |
| `/ok` | GET | 存活探针 |
| `/metrics` | GET | 基础指标 |

## 项目结构

```
harness-agent-system/
├── src/app/                    # 核心应用代码
│   ├── main.py                 # FastAPI 应用入口
│   ├── api/                    # API 端点
│   ├── agents/                 # Agent 工厂
│   ├── core/                   # 配置和状态管理
│   ├── middleware/             # 中间件
│   ├── mcp_server/             # MCP 服务器
│   ├── processors/             # PDF 处理器
│   ├── schema/                 # 请求/响应模型
│   ├── tools/                  # 工具集合
│   └── utils/                  # 工具函数
├── tests/                      # 测试套件
├── docs/                       # 文档
├── docker/                     # Docker 配置
├── scripts/                    # 开发脚本
├── data/                       # SQLite 数据文件
├── pyproject.toml              # 项目配置
└── Makefile                    # 开发命令
```

## 配置

所有配置通过环境变量管理，详见 `.env.example`：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | - |
| `VISION_API_KEY` | 火山引擎 API 密钥 | - |
| `API_KEY` | API 认证密钥 | - |
| `QWEN_API_KEY` | 通义千问 API 密钥 | - |
| `QWEN_BASE_URL` | 通义千问 API 地址 | https://dashscope.aliyuncs.com/compatible-mode/v1 |
| `QWEN_MODEL` | 通义千问模型 | qwen3.6-35b-a3b |
| `LOG_LEVEL` | 日志级别 | INFO |
| `SERVER_PORT` | 服务端口 | 2026 |

## 开发命令

```bash
make help           # 查看所有命令
make dev            # 启动开发服务器
make test           # 运行测试
make lint           # 代码检查
make format         # 代码格式化
make docker-build   # 构建 Docker 镜像
make docker-up      # 启动 Docker 服务
```

## 贡献指南

详见 [贡献指南](./贡献指南.md)

## 许可证

[MIT License](LICENSE)
