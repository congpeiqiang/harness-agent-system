# _*_ coding:utf-8_*_
import os
import base64
import uuid
from pathlib import Path
from typing import Callable, List, Dict, Any

from langgraph.types import Command
from langchain.agents.middleware import (
    AgentMiddleware,
    ExtendedModelResponse,
    ModelRequest,
    ModelResponse,
)
from langchain.messages import HumanMessage

from app.tools import parse_pdf_from_file
from app.logger import setup_logger

# 获取日志记录器
logger = setup_logger(__name__)


class PDFParseMiddleware(AgentMiddleware):
    def awrap_model_call(
            self,
            request: ModelRequest,
            handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """
        中间件函数，处理前端发送的消息，检查是否包含PDF文件，如果有则保存并调用PDF解析工具

        Args:
            request: 模型请求对象
            handler: 处理模型请求的回调函数

        Returns:
            扩展的模型响应对象
        """
        # 创建上传目录（如果不存在）
        messages = getattr(request, "messages", [])
        logger.info(f"调用中间件(PDFParseMiddleware)，处理前的消息数量: {len(messages)}")
        upload_dir = Path("uploads/pdf")
        upload_dir.mkdir(parents=True, exist_ok=True)

        # 获取请求中的消息和thread_id
        # 从runtime.execution_info中获取thread_id
        runtime = getattr(request, "runtime", None)
        if runtime:
            execution_info = getattr(runtime, "execution_info", None)
            if execution_info:
                thread_id = getattr(execution_info, "thread_id", str(uuid.uuid4()))
            else:
                thread_id = str(uuid.uuid4())
        else:
            thread_id = str(uuid.uuid4())

        logger.info(f"处理线程ID: {thread_id}")

        # 创建thread_id专属目录
        thread_dir = upload_dir / thread_id
        thread_dir.mkdir(parents=True, exist_ok=True)

        # 处理每个消息
        processed_messages = []
        for message in messages:
            # 创建消息副本以避免修改原始消息
            processed_message = message.copy()

            # 只处理HumanMessage
            if isinstance(message, HumanMessage):
                # 检查是否有附件
                additional_kwargs = message.additional_kwargs
                if "attachments" in additional_kwargs:
                    for attachment in additional_kwargs["attachments"]:
                        # 检查是否是PDF文件
                        if attachment.get("mimeType") == "application/pdf":
                            try:
                                # 获取原始文件名和base64数据
                                original_filename = attachment.get("metadata", {}).get("filename",
                                                                                       f"{uuid.uuid4()}.pdf")
                                base64_data = attachment.get("data", "")

                                logger.info(f"处理PDF文件: {original_filename}")

                                # 保留原始文件名，但确保文件名唯一
                                file_extension = os.path.splitext(original_filename)[1]
                                unique_filename = f"{original_filename}"
                                file_path = thread_dir / unique_filename

                                # 解码base64数据并保存文件
                                with open(file_path, "wb") as f:
                                    f.write(base64.b64decode(base64_data))

                                logger.info(f"PDF文件已保存到: {file_path}")

                                # 调用PDF解析工具
                                parsed_content = parse_pdf_from_file.invoke(str(file_path))

                                logger.info(f"PDF解析完成，内容长度: {len(parsed_content) if parsed_content else 0}")

                                # 将解析结果添加到消息内容中
                                if parsed_content:
                                    # 创建一个新的消息，包含原始内容和解析结果
                                    original_content = message.content
                                    new_content = f"{original_content}\n\n文档解析结果:\n{parsed_content}"
                                    processed_message.content = new_content
                            except Exception as e:
                                # 如果处理失败，添加错误信息到消息中
                                logger.error(f"PDF处理失败: {str(e)}", exc_info=True)
                                original_content = message.content
                                error_msg = f"\n\nPDF处理失败: {str(e)}"
                                processed_message.content = f"{original_content}{error_msg}"

            processed_messages.append(processed_message)

        logger.info(f"调用中间件(PDFParseMiddleware)，处理后的消息数量: {len(processed_messages)}")
        # 使用override方法更新请求中的消息
        request = request.override(messages=processed_messages)

        # 调用处理程序并返回结果
        return handler(request)

    def wrap_model_call(
            self,
            request: ModelRequest,
            handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """
        中间件函数，处理前端发送的消息，检查是否包含PDF文件，如果有则保存并调用PDF解析工具

        Args:
            request: 模型请求对象
            handler: 处理模型请求的回调函数

        Returns:
            扩展的模型响应对象
        """
        # 创建上传目录（如果不存在）
        messages = getattr(request, "messages", [])
        logger.info(f"调用中间件(PDFParseMiddleware)，处理前的消息数量: {len(messages)}")
        upload_dir = Path("uploads/pdf")
        upload_dir.mkdir(parents=True, exist_ok=True)

        # 获取请求中的消息和thread_id
        # 从runtime.execution_info中获取thread_id
        runtime = getattr(request, "runtime", None)
        if runtime:
            execution_info = getattr(runtime, "execution_info", None)
            if execution_info:
                thread_id = getattr(execution_info, "thread_id", str(uuid.uuid4()))
            else:
                thread_id = str(uuid.uuid4())
        else:
            thread_id = str(uuid.uuid4())

        logger.info(f"处理线程ID: {thread_id}")

        # 创建thread_id专属目录
        thread_dir = upload_dir / thread_id
        thread_dir.mkdir(parents=True, exist_ok=True)

        # 处理每个消息
        processed_messages = []
        for message in messages:
            # 创建消息副本以避免修改原始消息
            processed_message = message.copy()

            # 只处理HumanMessage
            if isinstance(message, HumanMessage):
                # 检查是否有附件
                additional_kwargs = message.additional_kwargs
                if "attachments" in additional_kwargs:
                    for attachment in additional_kwargs["attachments"]:
                        # 检查是否是PDF文件
                        if attachment.get("mimeType") == "application/pdf":
                            try:
                                # 获取原始文件名和base64数据
                                original_filename = attachment.get("metadata", {}).get("filename",
                                                                                       f"{uuid.uuid4()}.pdf")
                                base64_data = attachment.get("data", "")

                                logger.info(f"处理PDF文件: {original_filename}")

                                # 保留原始文件名，但确保文件名唯一
                                file_extension = os.path.splitext(original_filename)[1]
                                unique_filename = f"{original_filename}"
                                file_path = thread_dir / unique_filename

                                # 解码base64数据并保存文件
                                with open(file_path, "wb") as f:
                                    f.write(base64.b64decode(base64_data))

                                logger.info(f"PDF文件已保存到: {file_path}")

                                # 调用PDF解析工具
                                parsed_content = parse_pdf_from_file.invoke(str(file_path))

                                logger.info(f"PDF解析完成，内容长度: {len(parsed_content) if parsed_content else 0}")

                                # 将解析结果添加到消息内容中
                                if parsed_content:
                                    # 创建一个新的消息，包含原始内容和解析结果
                                    original_content = message.content
                                    new_content = f"{original_content}\n\n文档解析结果:\n{parsed_content}"
                                    processed_message.content = new_content
                            except Exception as e:
                                # 如果处理失败，添加错误信息到消息中
                                logger.error(f"PDF处理失败: {str(e)}", exc_info=True)
                                original_content = message.content
                                error_msg = f"\n\nPDF处理失败: {str(e)}"
                                processed_message.content = f"{original_content}{error_msg}"

            processed_messages.append(processed_message)

        logger.info(f"调用中间件(PDFParseMiddleware)，处理后的消息数量: {len(processed_messages)}")
        # 使用override方法更新请求中的消息
        request = request.override(messages=processed_messages)

        # 调用处理程序并返回结果
        return handler(request)
