# StreamingResponse 日志管理实现逻辑

## 概述

本文档详细说明 `StreamingResponse` 项目中**生产级日志管理**的实现逻辑。核心目标是让 Uvicorn 访问日志、应用业务日志、错误日志都按天写入不同文件，同时保留控制台输出，便于开发和运维排查问题。

---

## 一、日志文件结构

运行后自动生成 `logs/` 目录，按天切分文件：

```
logs/
├── app_2026-06-17.log      # 应用业务日志（Agent处理、请求追踪）
├── access_2026-06-17.log   # HTTP 访问日志（Uvicorn 自动记录）
└── error_2026-06-17.log    # 错误日志（异常、端口冲突等）
```

**设计理由**：
- 分离不同日志类型，便于定向排查（业务问题看 `app`，流量分析看 `access`）
- 按天切分避免单文件过大，同时方便按日期清理
- 默认保留最近 **30 天** 日志，自动删除过期文件

---

## 二、核心架构

整个日志系统分为两层：

| 层级 | 文件 | 职责 |
|------|------|------|
| **配置层** | `log_config.py` | 定义日志格式、轮转策略、文件分配 |
| **应用层** | `main.py` | 在业务逻辑中埋点，记录请求全链路 |

---

## 三、配置层详解（`log_config.py`）

### 3.1 自定义按天轮转处理器

```python
class DailyRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    def __init__(self, log_dir: str, filename_prefix: str = "app", backup_count: int = 30):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 文件名格式：app_2026-06-17.log
        self.log_file = self.log_dir / f"{filename_prefix}_{datetime.now().strftime('%Y-%m-%d')}.log"
        
        super().__init__(
            filename=str(self.log_file),
            when="midnight",           # 每天午夜自动轮转
            interval=1,
            backupCount=backup_count,   # 保留 30 天
            encoding="utf-8",
        )
```

**关键点**：
- 继承 Python 内置的 `TimedRotatingFileHandler`，利用其 `when="midnight"` 机制，在每天 00:00 自动创建新文件
- 文件名硬编码日期，避免轮转后文件名混乱
- `backupCount=30` 确保磁盘不会无限增长，过期日志自动清理

### 3.2 统一配置入口

```python
def setup_logging(log_dir=None, log_level="INFO", ..., console_output=True, json_format=False):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 清除已有处理器（避免重复添加）
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 1. 文件处理器（按天轮转）
    file_handler = DailyRotatingFileHandler(...)
    root_logger.addHandler(file_handler)
    
    # 2. 控制台处理器（同时打印到终端）
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        root_logger.addHandler(console_handler)
```

**为什么先清除已有处理器？**

Uvicorn 或第三方库在导入时可能已经注册了默认处理器，如果不清理，会导致同一条日志既走 Uvicorn 默认路径，又走我们的自定义路径，最终**重复打印**。

### 3.3 Uvicorn 日志隔离（关键设计）

```python
# 访问日志 -> 单独文件
access_logger = logging.getLogger("uvicorn.access")
access_logger.handlers = []              # 清空默认
access_logger.addHandler(access_handler)  # 只写入 access_日期.log
access_logger.propagate = False          # 阻断向上传播，防止重复

# 错误日志 -> 文件 + 控制台
uvicorn_logger = logging.getLogger("uvicorn.error")
uvicorn_logger.handlers = []
uvicorn_logger.addHandler(error_handler)   # 写入 error_日期.log
uvicorn_logger.addHandler(console_handler) # 控制台也显示
uvicorn_logger.propagate = False
```

**核心设计意图**：

| 日志器名称 | 说明 | 输出位置 |
|-----------|------|---------|
| `uvicorn.access` | Uvicorn 内部 HTTP 访问日志 | `access_日期.log` |
| `uvicorn.error` | Uvicorn 内部错误/启动日志 | `error_日期.log` + 控制台 |
| 根日志器 | 应用业务日志 | `app_日期.log` + 控制台 |

`propagate = False` 是核心：如果不阻断，Uvicorn 的日志会向上传递给根日志器，导致一条日志既写入 `access.log` 又写入 `app.log`。

### 3.4 Uvicorn 启动配置字典

```python
def get_uvicorn_log_config(log_dir):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "default": {"filename": "app_日期.log", ...},
            "access": {"filename": "access_日期.log", ...},
            "console": {"class": "logging.StreamHandler", ...},
        },
        "loggers": {
            "uvicorn": {"handlers": ["default", "console"], ...},
            "uvicorn.access": {"handlers": ["access", "console"], ...},
            "uvicorn.error": {"handlers": ["default", "console"], ...},
        }
    }
```

这个字典直接传给 `uvicorn.run(log_config=...)`，确保 Uvicorn 自己的日志（启动信息、请求记录）也走我们的文件，而不是默认的 stderr。

---

## 四、应用层详解（`main.py`）

### 4.1 初始化日志

```python
LOG_DIR = Path(__file__).parent / "logs"

setup_logging(
    log_dir=LOG_DIR,
    log_level="INFO",
    filename_prefix="app",
    backup_count=30,
    console_output=True,
)

logger = logging.getLogger(__name__)
```

**执行时机**：模块导入时立即执行，保证所有后续代码都使用这个配置。

### 4.2 请求追踪中间件（核心）

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    request_id = str(uuid.uuid4())[:8]  # 生成 8 位短 ID
    
    # 请求开始时记录
    logger.info(
        f"[Req:{request_id}] {request.method} {request.url.path} "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
    
    try:
        response = await call_next(request)
        elapsed = (time.time() - start_time) * 1000
        # 请求结束时记录状态码和耗时
        logger.info(
            f"[Req:{request_id}] {request.method} {request.url.path} "
            f"-> {response.status_code} ({elapsed:.2f}ms)"
        )
        return response
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error(
            f"[Req:{request_id}] {request.method} {request.url.path} "
            f"-> ERROR ({elapsed:.2f}ms): {str(e)}"
        )
        raise
```

**设计价值**：
- 每个 HTTP 请求自动生成 `request_id`（如 `e1ec8678`），串联请求生命周期
- 记录请求方法、路径、客户端 IP、响应状态码、耗时
- 异常时自动捕获并记录，无需在每个接口写 try/except

### 4.3 业务逻辑埋点

```python
async def stream_response(self, message: str, request_id: str):
    logger.info(f"[Req:{request_id}] 开始处理请求，消息长度: {len(message)} 字符")
    
    # ... 生成内容 ...
    
    logger.info(f"[Req:{request_id}] 生成完成，共 {len(words)} 个token")
    logger.info(f"[Req:{request_id}] 请求处理完成，总计请求数: {self.request_count}")
```

**关键设计**：所有业务日志都带上 `[Req:{request_id}]`，通过 grep 可以追踪一个请求的完整链路：

```bash
grep "Req:e1ec8678" logs/app_2026-06-17.log
```

### 4.4 启动时传入日志配置

```python
log_config = get_uvicorn_log_config(LOG_DIR)
uvicorn.run(
    "main:app",
    host="0.0.0.0",
    port=8000,
    log_config=log_config,  # 覆盖 Uvicorn 默认日志
    access_log=True,
)
```

---

## 五、日志流转全景图

```
                    HTTP 请求进入
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
    ▼                    ▼                    ▼
请求中间件          业务函数处理          Uvicorn 访问记录
  │                    │                    │
  │ 生成 request_id    │ logger.info(...)   │ 127.0.0.1 - "POST /chat"
  │                    │                    │
  └────────────────────┼────────────────────┘
                       │
                       ▼
         ┌─────────────┼─────────────┐
         │             │             │
    [控制台]    [app_日期.log]   [access_日期.log]
    (开发看)      (业务追踪)       (流量分析)
         │             │             │
         └─────────────┴─────────────┘
                       │
              [error_日期.log]
              (异常/错误记录)
```

---

## 六、日志格式说明

### 统一格式

```
2026-06-17 20:03:57 | INFO     | main:80 | [Req:b3a34bfb] 开始处理请求，消息长度: 6 字符
```

| 字段 | 含义 |
|------|------|
| `2026-06-17 20:03:57` | 时间戳 |
| `INFO` | 日志级别（DEBUG/INFO/WARNING/ERROR） |
| `main:80` | 模块名:行号，快速定位代码位置 |
| `[Req:b3a34bfb]` | 请求 ID，串联全链路 |
| `开始处理请求...` | 业务信息 |

---

## 七、生产环境适配建议

| 场景 | 配置调整 | 说明 |
|------|---------|------|
| 减少日志量 | `log_level="WARNING"` | 只记录警告和错误 |
| 接入日志收集系统（ELK/Loki） | `json_format=True` | 输出 JSON 格式，便于解析 |
| 日志目录挂载到宿主机 | `log_dir="/var/log/agent"` | 容器退出后日志不丢失 |
| 延长保留时间 | `backup_count=90` | 保留 90 天 |
| 纯容器环境（无终端） | `console_output=False` | 只写文件，不打印控制台 |

---

## 八、常见问题排查

### 问题 1：日志没有写入文件

检查 `setup_logging()` 是否在模块导入时执行。如果放在函数内部，只有调用函数时才生效，之前的日志会丢失。

### 问题 2：日志重复打印

检查是否忘记设置 `propagate = False`。Uvicorn 日志默认会向上传播到根日志器，导致一条日志被多个处理器处理。

### 问题 3：中文显示乱码

检查 `encoding="utf-8"` 是否设置。Windows 环境下如果省略，可能使用系统默认编码（GBK）导致中文乱码。

### 问题 4：日志文件不轮转

`TimedRotatingFileHandler` 依赖程序持续运行到午夜。如果进程频繁重启，可以考虑改用 `RotatingFileHandler`（按文件大小轮转）。

---

## 九、文件清单

| 文件 | 说明 |
|------|------|
| `log_config.py` | 日志配置模块，独立可复用 |
| `main.py` | FastAPI 应用，集成日志埋点 |
| `logs/` | 日志输出目录，自动生成 |
