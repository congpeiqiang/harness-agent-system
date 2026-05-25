"""
@File    :   docling_pdf_parser_demo.py
@Author  :   CodeGeeX
@Time    :   2026/5/25
@Desc    :   Docling PDF 解析器演示脚本

使用方法（支持直接运行和模块运行）:
    1. 直接运行（推荐）:
       python src/app/examples/docling_pdf_parser_demo.py
       python src/app/examples/docling_pdf_parser_demo.py --file /path/to/your.pdf
       python src/app/examples/docling_pdf_parser_demo.py --url https://patentimages.storage.googleapis.com/aa/80/e5/7ef9a628254e36/CN1406291A.pdf

    2. 模块运行:
       python -m src.app.examples.docling_pdf_parser_demo
       python -m src.app.examples.docling_pdf_parser_demo --file /path/to/your.pdf
       python -m src.app.examples.docling_pdf_parser_demo --url https://example.com/doc.pdf

    3. 测试 base64 内容解析:
       python src/app/examples/docling_pdf_parser_demo.py --base64

    4. 组合使用:
       python src/app/examples/docling_pdf_parser_demo.py --url https://example.com/doc.pdf --base64 --export-types
"""

import argparse
import base64
import os
import sys
import time
import tempfile
import requests
from urllib.parse import urlparse

# 添加项目根目录到 Python 路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 同时添加 src 目录到路径
src_dir = os.path.join(project_root, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from app.processors.docling_pdf_parser import DoclingPDFParser
from app.tools.docling_pdf_tool import (
    docling_parse_pdf_from_file,
    docling_parse_pdf_from_content,
    docling_parse_pdf_from_url,
)
from app.logger import setup_logger

logger = setup_logger(__name__)


def is_url(path_or_url: str) -> bool:
    """判断是否为 URL"""
    parsed = urlparse(path_or_url)
    return parsed.scheme in ("http", "https") and parsed.netloc


def download_pdf(url: str, timeout: int = 60) -> str:
    """下载在线 PDF 到临时文件
    
    Args:
        url: PDF 文件的 URL
        timeout: 下载超时时间（秒）
        
    Returns:
        临时文件路径
        
    Raises:
        Exception: 下载失败
    """
    print(f"正在下载 PDF: {url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        response.raise_for_status()
        
        # 获取文件大小
        total_size = int(response.headers.get("content-length", 0))
        print(f"文件大小: {total_size / 1024 / 1024:.2f} MB")
        
        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        
        downloaded = 0
        chunk_size = 8192
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                temp_file.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"下载进度: {percent:.1f}%", end="\r")
        
        temp_file.close()
        print(f"\n下载完成: {temp_file.name}")
        return temp_file.name
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"下载 PDF 失败: {e}")


def find_sample_pdf():
    """查找示例 PDF 文件"""
    possible_paths = [
        os.path.join(project_root, "uploads", "pdf", "sample.pdf"),
        os.path.join(project_root, "uploads", "pdf"),
    ]
    
    for path in possible_paths:
        if os.path.isfile(path) and path.lower().endswith(".pdf"):
            return path
        elif os.path.isdir(path):
            for file in os.listdir(path):
                if file.lower().endswith(".pdf"):
                    return os.path.join(path, file)
    
    return None


def test_docling_parser_class(pdf_path: str, is_temp: bool = False):
    """测试 DoclingPDFParser 类"""
    print("\n" + "=" * 60)
    print("测试 1: DoclingPDFParser 类 - parse_file 方法")
    print("=" * 60)
    
    parser = DoclingPDFParser()
    
    start_time = time.time()
    docs = parser.parse_file(pdf_path)
    first_parse_time = time.time() - start_time
    
    print(f"\n首次解析:")
    print(f"  耗时: {first_parse_time:.2f} 秒")
    print(f"  文档片段数: {len(docs)}")
    print(f"  第一片段内容预览 (前 500 字符):")
    if docs:
        content_preview = docs[0].page_content[:500] + "..." if len(docs[0].page_content) > 500 else docs[0].page_content
        print(f"  {content_preview}")
        print(f"  元数据: {docs[0].metadata}")
    
    start_time = time.time()
    docs_cached = parser.parse_file(pdf_path)
    second_parse_time = time.time() - start_time
    
    print(f"\n缓存解析:")
    print(f"  耗时: {second_parse_time:.4f} 秒")
    print(f"  文档片段数: {len(docs_cached)}")
    
    parser.clear_cache()
    print("\n缓存已清除")
    
    # 清理临时文件
    if is_temp and os.path.exists(pdf_path):
        os.remove(pdf_path)
        print(f"临时文件已删除: {pdf_path}")
    
    return docs


def test_docling_base64_parser(pdf_path: str, is_temp: bool = False):
    """测试从 base64 内容解析"""
    print("\n" + "=" * 60)
    print("测试 2: DoclingPDFParser 类 - parse_content 方法 (base64)")
    print("=" * 60)
    
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
    
    print(f"\n文件大小: {len(pdf_bytes)} bytes")
    print(f"Base64 长度: {len(pdf_base64)} characters")
    
    parser = DoclingPDFParser()
    
    start_time = time.time()
    docs = parser.parse_content(pdf_base64)
    parse_time = time.time() - start_time
    
    print(f"\n解析结果:")
    print(f"  耗时: {parse_time:.2f} 秒")
    print(f"  文档片段数: {len(docs)}")
    if docs:
        print(f"  总字符数: {sum(len(doc.page_content) for doc in docs)}")
    
    if is_temp and os.path.exists(pdf_path):
        os.remove(pdf_path)
        print(f"临时文件已删除: {pdf_path}")
    
    return docs


def test_docling_tools(pdf_path: str, is_temp: bool = False):
    """测试 Docling Tool 函数"""
    print("\n" + "=" * 60)
    print("测试 3: Docling Tool 函数")
    print("=" * 60)
    
    print("\n--- docling_parse_pdf_from_file ---")
    start_time = time.time()
    result = docling_parse_pdf_from_file.invoke({"file_name": pdf_path})
    tool_time = time.time() - start_time
    
    print(f"耗时: {tool_time:.2f} 秒")
    print(f"返回文本长度: {len(result)} characters")
    print(f"内容预览 (前 500 字符):")
    preview = result[:500] + "..." if len(result) > 500 else result
    print(preview)
    
    print("\n--- 缓存测试 (第二次调用) ---")
    start_time = time.time()
    result_cached = docling_parse_pdf_from_file.invoke({"file_name": pdf_path})
    cached_time = time.time() - start_time
    print(f"缓存调用耗时: {cached_time:.4f} 秒")
    
    if is_temp and os.path.exists(pdf_path):
        os.remove(pdf_path)
        print(f"\n临时文件已删除: {pdf_path}")


def test_docling_url_parser(url: str):
    """测试 DoclingPDFParser 类 - parse_url 方法"""
    print("\n" + "=" * 60)
    print("测试 5: DoclingPDFParser 类 - parse_url 方法")
    print("=" * 60)
    
    parser = DoclingPDFParser()
    
    print(f"\n直接解析在线 PDF: {url}")
    start_time = time.time()
    docs = parser.parse_url(url)
    first_parse_time = time.time() - start_time
    
    print(f"\n首次解析:")
    print(f"  耗时: {first_parse_time:.2f} 秒")
    print(f"  文档片段数: {len(docs)}")
    if docs:
        content_preview = docs[0].page_content[:500] + "..." if len(docs[0].page_content) > 500 else docs[0].page_content
        print(f"  第一片段内容预览 (前 500 字符):")
        print(f"  {content_preview}")
    
    # 缓存测试
    start_time = time.time()
    docs_cached = parser.parse_url(url)
    second_parse_time = time.time() - start_time
    
    print(f"\n缓存解析:")
    print(f"  耗时: {second_parse_time:.4f} 秒")
    print(f"  文档片段数: {len(docs_cached)}")
    
    parser.clear_cache()
    print("\n缓存已清除")
    
    return docs


def test_docling_url_tool(url: str):
    """测试 Docling URL Tool 函数"""
    print("\n" + "=" * 60)
    print("测试 6: Docling URL Tool 函数")
    print("=" * 60)
    
    print(f"\n--- docling_parse_pdf_from_url ---")
    start_time = time.time()
    result = docling_parse_pdf_from_url.invoke({"url": url})
    tool_time = time.time() - start_time
    
    print(f"耗时: {tool_time:.2f} 秒")
    print(f"返回文本长度: {len(result)} characters")
    print(f"内容预览 (前 500 字符):")
    preview = result[:500] + "..." if len(result) > 500 else result
    print(preview)
    
    print("\n--- 缓存测试 (第二次调用) ---")
    start_time = time.time()
    result_cached = docling_parse_pdf_from_url.invoke({"url": url})
    cached_time = time.time() - start_time
    print(f"缓存调用耗时: {cached_time:.4f} 秒")


def test_export_types(pdf_path: str, is_temp: bool = False):
    """测试不同的导出类型"""
    print("\n" + "=" * 60)
    print("测试 4: 不同导出类型")
    print("=" * 60)
    
    print("\n--- Markdown 导出 ---")
    parser_md = DoclingPDFParser(export_type="markdown")
    docs_md = parser_md.parse_file(pdf_path)
    if docs_md:
        print(f"片段数: {len(docs_md)}")
        print(f"内容预览 (前 300 字符):")
        preview = docs_md[0].page_content[:300] + "..." if len(docs_md[0].page_content) > 300 else docs_md[0].page_content
        print(preview)
    
    print("\n--- Document 导出 ---")
    parser_doc = DoclingPDFParser(export_type="document")
    docs_doc = parser_doc.parse_file(pdf_path)
    if docs_doc:
        print(f"片段数: {len(docs_doc)}")
        print(f"内容预览 (前 300 字符):")
        preview = docs_doc[0].page_content[:300] + "..." if len(docs_doc[0].page_content) > 300 else docs_doc[0].page_content
        print(preview)
    
    if is_temp and os.path.exists(pdf_path):
        os.remove(pdf_path)
        print(f"\n临时文件已删除: {pdf_path}")


def main():
    parser = argparse.ArgumentParser(description="Docling PDF 解析器演示")
    parser.add_argument(
        "--file",
        type=str,
        help="指定要解析的 PDF 文件路径"
    )
    parser.add_argument(
        "--url",
        type=str,
        help="指定要解析的在线 PDF URL"
    )
    parser.add_argument(
        "--base64",
        action="store_true",
        help="测试 base64 内容解析"
    )
    parser.add_argument(
        "--export-types",
        action="store_true",
        help="测试不同导出类型"
    )
    
    args = parser.parse_args()
    
    pdf_path = None
    is_temp_file = False
    
    # 处理 URL
    if args.url:
        if not is_url(args.url):
            print(f"错误: 无效的 URL: {args.url}")
            sys.exit(1)
        pdf_path = download_pdf(args.url)
        is_temp_file = True
    # 处理本地文件
    elif args.file:
        if is_url(args.file):
            print("检测到 URL，请使用 --url 参数指定在线 PDF")
            sys.exit(1)
        pdf_path = args.file
        if not os.path.isfile(pdf_path):
            print(f"错误: 文件不存在: {pdf_path}")
            sys.exit(1)
    else:
        pdf_path = find_sample_pdf()
        if not pdf_path:
            print("错误: 未找到示例 PDF 文件")
            print(f"请在 {os.path.join(project_root, 'uploads', 'pdf')} 目录下放置一个 PDF 文件")
            print("或使用 --file 或 --url 参数指定 PDF")
            sys.exit(1)
    
    print(f"\n使用 PDF 文件: {pdf_path}")
    if args.url:
        print(f"来源 URL: {args.url}")
    
    try:
        test_docling_parser_class(pdf_path, is_temp_file)
        
        if args.base64:
            test_docling_base64_parser(pdf_path, is_temp_file)
            is_temp_file = False
        
        test_docling_tools(pdf_path, is_temp_file)
        is_temp_file = False
        
        if args.export_types:
            test_export_types(pdf_path, is_temp_file)
            is_temp_file = False
        
        # 如果指定了 URL，额外测试 URL 直接解析
        if args.url:
            test_docling_url_parser(args.url)
            test_docling_url_tool(args.url)
        
        if is_temp_file and os.path.exists(pdf_path):
            os.remove(pdf_path)
            print(f"\n临时文件已删除: {pdf_path}")
        
        print("\n" + "=" * 60)
        print("所有测试完成!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n错误: {e}")
        logger.error("测试失败", exc_info=True)
        if is_temp_file and pdf_path and os.path.exists(pdf_path):
            os.remove(pdf_path)
            print(f"临时文件已删除: {pdf_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
