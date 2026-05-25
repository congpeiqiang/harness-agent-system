# _*_ coding:utf-8_*_
# src/app/logger/logger_config.py
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# 日志目录
LOG_DIR = Path("D:/workspace/huice_008/harness-agent-system/src/app/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)


def setup_logger(name: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    设置并返回一个日志记录器

    Args:
        name: 日志记录器名称，通常使用 __name__
        level: 日志级别，默认为 INFO

    Returns:
        配置好的日志记录器
    """
    # 如果没有提供名称，使用调用者的模块名
    if name is None:
        name = "app"

    # 创建日志记录器
    logger = logging.getLogger(name)

    # 避免重复添加处理器
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # 创建文件处理器，按天轮转
    file_handler = TimedRotatingFileHandler(
        filename=LOG_DIR / f"{name}.log",
        when="midnight",
        interval=1,
        backupCount=30,  # 保留30天的日志
        encoding="utf-8"
    )
    file_handler.setLevel(level)

    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 添加处理器到日志记录器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# 创建默认日志记录器
default_logger = setup_logger("app")
