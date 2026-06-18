# Harness Agent System API 测试套件

## 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行单元测试
uv run pytest tests/unit/

# 运行集成测试
uv run pytest tests/integration/

# 查看覆盖率
uv run pytest --cov=app --cov-report=term-missing
```

## 测试结构

```
tests/
├── unit/                    # 单元测试
│   ├── test_config.py       # 配置测试
│   ├── test_api.py          # API 端点测试
│   ├── test_schema.py       # Schema 测试
│   ├── test_weather_tool.py # 天气工具测试
│   └── test_pdf_tool.py     # PDF 工具测试
├── integration/             # 集成测试
├── conftest.py              # 共享 fixtures
└── test_server.py           # 服务器集成测试
```

## 编写测试

1. 单元测试放在 `tests/unit/` 目录
2. 集成测试放在 `tests/integration/` 目录
3. 测试文件命名为 `test_*.py`
4. 测试函数命名为 `test_*`
5. 使用 pytest fixtures 共享测试数据
