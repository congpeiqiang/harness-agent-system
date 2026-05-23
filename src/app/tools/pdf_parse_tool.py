"""
@File    :  pdf_parse_tool.py
@Author  :  CongPeiQiang
@Time    :  2026/5/22 14:07
@Desc    :  
"""
import tempfile

from app.processors import PDFParser, _compute_file_hash, _compute_bytes_hash, _decode_content, _do_parse_pdf_from_file
from langchain.tools import tool
from app.core.config import settings
import logging

# 1. 配置 logging (只需在程序入口配置一次)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 2. 获取 logger 实例
# 建议传入 __name__，这样可以看到日志是来自哪个模块
logger = logging.getLogger(__name__)

# 模块级共享 PDFParser 实例，供 @tool 函数使用缓存
_shared_parser = PDFParser()

@tool
def parse_pdf_from_file(file_path: str) -> str:
    """从文件路径解析 PDF，返回解析后的纯文本内容。

    解析配置（mode、table_strategy、enable_multimodal 等）从 settings 自动读取。
    同一文件（基于内容哈希判断）不会重复解析，直接返回缓存结果。

    Args:
        file_path: PDF 文件绝对路径

    Returns:
        解析后的纯文本内容
    """
    file_hash = _compute_file_hash(file_path)

    # 命中缓存
    if file_hash in _shared_parser._cache:
        logger.info("命中缓存，跳过解析 | 文件: %s | 哈希: %s", file_path, file_hash[:12])
        docs = _shared_parser._cache[file_hash]
    else:
        docs = _do_parse_pdf_from_file(
            file_path,
            mode=settings.pdf_mode,
            table_strategy=settings.pdf_table_strategy,
            enable_multimodal=settings.enable_pdf_multimodal,
            extract_images=settings.pdf_extract_images,
        )
        _shared_parser._evict_if_needed()
        _shared_parser._cache[file_hash] = docs
        logger.info("解析完成并缓存 | 文件: %s | 哈希: %s | 片段数: %d", file_path, file_hash[:12], len(docs))

    return "\n\n".join(doc.page_content for doc in docs)


@tool
def parse_pdf_from_content(content: str) -> str:
    """从 base64 编码内容解析 PDF，返回解析后的纯文本内容。

    解析配置（mode、table_strategy、enable_multimodal 等）从 settings 自动读取。
    同一内容（基于哈希判断）不会重复解析，直接返回缓存结果。

    Args:
        content: base64 编码的 PDF 内容字符串

    Returns:
        解析后的纯文本内容
    """
    pdf_bytes = _decode_content(content)
    content_hash = _compute_bytes_hash(pdf_bytes)

    # 命中缓存
    if content_hash in _shared_parser._cache:
        logger.info("命中缓存，跳过解析 | 哈希: %s", content_hash[:12])
        docs = _shared_parser._cache[content_hash]
    else:
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(pdf_bytes)
                tmp_path = tmp.name

            docs = _do_parse_pdf_from_file(
                tmp_path,
                mode=settings.pdf_mode,
                table_strategy=settings.pdf_table_strategy,
                enable_multimodal=settings.enable_pdf_multimodal,
                extract_images=settings.pdf_extract_images,
            )
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
                logger.debug("已清理临时文件: %s", tmp_path)

        _shared_parser._evict_if_needed()
        _shared_parser._cache[content_hash] = docs
        logger.info("解析完成并缓存 | 哈希: %s | 片段数: %d", content_hash[:12], len(docs))

    return "\n\n".join(doc.page_content for doc in docs)