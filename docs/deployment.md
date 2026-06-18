# 部署指南

## 前置条件

- Python 3.13.5
- Docker 和 Docker Compose（用于容器化部署）
- uv 包管理器（推荐）

## 本地开发

### 1. 克隆并搭建环境

```bash
git clone https://github.com/your-org/harness-agent-system.git
cd harness-agent-system

# 安装依赖
uv sync

# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API 密钥
```

### 2. 启动开发服务器

```bash
# 使用 Make
make dev

# 或直接运行
uvicorn app.main:app --reload --host 0.0.0.0 --port 2026
```

### 3. 运行测试

```bash
make test
```

## Docker 部署

### 构建镜像

```bash
# 使用 Make
make docker-build

# 或直接构建
docker build -f docker/Dockerfile -t harness-agent-system:latest .
```

### 开发环境 Docker Compose

```bash
# 启动服务
make docker-up

# 查看日志
make docker-logs

# 停止服务
make docker-down
```

### 生产环境部署

```bash
# 使用生产 compose 文件
docker-compose -f docker/docker-compose.prod.yml up -d

# 或使用 Make
make docker-prod-up
```

## 环境变量

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `DEEPSEEK_API_KEY` | 是 | - | DeepSeek API 密钥 |
| `VISION_API_KEY` | 否 | - | 火山引擎 API 密钥 |
| `API_KEY` | 否 | - | API 认证密钥 |
| `LOG_LEVEL` | 否 | INFO | 日志级别 (DEBUG/INFO/WARNING/ERROR) |
| `SERVER_PORT` | 否 | 2026 | 服务器端口 |
| `CORS_ORIGINS` | 否 | localhost:3000 | 允许的 CORS 来源 |
| `RATE_LIMIT_PER_MINUTE` | 否 | 60 | 每 IP 每分钟速率限制 |

## 生产环境检查清单

- [ ] 设置强密码 `API_KEY` 用于认证
- [ ] 配置 `CORS_ORIGINS` 为你的域名
- [ ] 设置合适的 `RATE_LIMIT_PER_MINUTE`
- [ ] 生产环境使用 `LOG_LEVEL=WARNING`
- [ ] 通过反向代理启用 HTTPS (nginx/traefik)
- [ ] 配置 `data/` 目录的数据库备份
- [ ] 在 `docker-compose.prod.yml` 中设置资源限制
- [ ] 配置健康检查监控

## 反向代理配置 (nginx)

```nginx
server {
    listen 80;
    server_name agent.example.com;

    location / {
        proxy_pass http://localhost:2026;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE 支持
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding off;
    }
}
```
