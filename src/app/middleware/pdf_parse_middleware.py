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
    def _extract_thread_id(self, request: ModelRequest) -> str:
        """
        从请求中提取thread_id
        
        Args:
            request: 模型请求对象
            
        Returns:
            thread_id字符串
        """
        runtime = getattr(request, "runtime", None)
        if runtime:
            execution_info = getattr(runtime, "execution_info", None)
            if execution_info:
                thread_id = getattr(execution_info, "thread_id", None)
                if thread_id:
                    return thread_id
        return str(uuid.uuid4())

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
        messages = getattr(request, "messages", [])
        logger.info(f"调用中间件(PDFParseMiddleware)异步，处理前的消息数量: {len(messages)}")

        # 先检查是否存在PDF附件
        has_pdf = False
        for message in messages:
            if isinstance(message, HumanMessage):
                additional_kwargs = getattr(message, "additional_kwargs", {})
                if "attachments" in additional_kwargs:
                    for attachment in additional_kwargs["attachments"]:
                        if attachment.get("mimeType") == "application/pdf":
                            has_pdf = True
                            break
                    if has_pdf:
                        break

        # 如果没有PDF附件，直接返回
        if not has_pdf:
            return handler(request)

        # 获取thread_id并创建目录结构: uploads/{thread_id}/pdf
        thread_id = self._extract_thread_id(request)
        logger.info(f"处理线程ID: {thread_id}")

        # 创建thread_id专属目录结构
        thread_dir = Path(f"uploads/{thread_id}/pdf")
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

                                # 保留原始文件名
                                file_path = thread_dir / original_filename

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

        logger.info(f"调用中间件(PDFParseMiddleware)异步，处理后的消息数量: {len(processed_messages)}")
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
        messages = getattr(request, "messages", [])
        logger.info(f"调用中间件(PDFParseMiddleware)，处理前的消息数量: {len(messages)}")

        # 先检查是否存在PDF附件
        has_pdf = False
        for message in messages:
            if isinstance(message, HumanMessage):
                additional_kwargs = getattr(message, "additional_kwargs", {})
                if "attachments" in additional_kwargs:
                    for attachment in additional_kwargs["attachments"]:
                        if attachment.get("mimeType") == "application/pdf":
                            has_pdf = True
                            break
                    if has_pdf:
                        break

        # 如果没有PDF附件，直接返回
        if not has_pdf:
            return handler(request)

        # 获取thread_id并创建目录结构: uploads/{thread_id}/pdf
        thread_id = self._extract_thread_id(request)
        logger.info(f"处理线程ID: {thread_id}")

        # 创建thread_id专属目录结构
        thread_dir = Path(f"uploads/{thread_id}/pdf")
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

                                # 保留原始文件名
                                file_path = thread_dir / original_filename

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
