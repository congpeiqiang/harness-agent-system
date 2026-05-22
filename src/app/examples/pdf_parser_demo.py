"""
PDF 解析器使用示例

演示专业 PDF 解析器的各种功能:
    1. 基础解析（仅文本）
    2. 多模态解析（包含图像识别）
    3. 缓存机制演示
    4. 解析后获取纯文本
    5. 通过 base64 内容解析
    6. 直接调用 @tool 函数（无缓存）
"""

import base64
import logging

# 配置日志级别
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from app.processors.pdf_parser import PDFParser, parse_pdf_from_file, parse_pdf_from_content

# ==================== 示例 1: 基础解析（仅文本） ====================
print("=" * 60)
print("示例 1: 基础解析（仅文本）")
print("=" * 60)

parser_basic = PDFParser(
    mode="single",
    table_strategy="lines",
    enable_multimodal=False  # 关闭多模态
)

file_path = "旅行日记.pdf"

try:
    # 第一次解析 - 会从文件加载
    print("\n第一次解析...")
    docs1 = parser_basic.parse_file(file_path)
    print(f"解析完成，内容长度: {len(docs1[0].page_content)} 字符")

    # 第二次解析 - 会命中缓存
    print("\n第二次解析（应该命中缓存）...")
    docs2 = parser_basic.parse_file(file_path)
    print(f"解析完成，内容长度: {len(docs2[0].page_content)} 字符")

    # 验证缓存生效：两次结果一致
    print(f"\n两次解析结果一致: {docs1[0].page_content == docs2[0].page_content}")

except FileNotFoundError:
    print(f"文件不存在: {file_path}")
    print("请确保 PDF 文件存在后再运行示例")


# ==================== 示例 2: 多模态解析 ====================
print("\n" + "=" * 60)
print("示例 2: 多模态解析（包含图像识别）")
print("=" * 60)

parser_multimodal = PDFParser(
    mode="single",
    table_strategy="lines",
    enable_multimodal=True,  # 开启多模态
    extract_images=True
)

try:
    print("\n多模态解析 PDF...")
    docs = parser_multimodal.parse_file(file_path)
    print(f"解析完成，内容长度: {len(docs[0].page_content)} 字符")

    # 打印部分内容
    print("\n前 500 字符内容预览:")
    print("-" * 40)
    print(docs[0].page_content[:500])
    print("-" * 40)

except FileNotFoundError:
    print(f"文件不存在: {file_path}")
except Exception as e:
    print(f"多模态解析失败: {e}")
    print("请确保 VISION_API_KEY 等环境变量已配置")


# ==================== 示例 3: 缓存管理 ====================
print("\n" + "=" * 60)
print("示例 3: 缓存管理")
print("=" * 60)

# 清除所有缓存
print("\n清除所有缓存...")
parser_basic.clear_cache()
print("缓存已清除")


# ==================== 示例 4: 解析后获取纯文本 ====================
print("\n" + "=" * 60)
print("示例 4: 解析后获取纯文本")
print("=" * 60)

try:
    parser = PDFParser(enable_multimodal=False)
    docs = parser.parse_file(file_path)
    text = "\n\n".join(doc.page_content for doc in docs)
    print(f"提取的纯文本长度: {len(text)} 字符")
    print("\n前 300 字符预览:")
    print("-" * 40)
    print(text[:300])
    print("-" * 40)

except FileNotFoundError:
    print(f"文件不存在: {file_path}")


# ==================== 示例 5: 通过 base64 内容解析 ====================
print("\n" + "=" * 60)
print("示例 5: 通过 base64 内容解析")
print("=" * 60)

try:
    # 先读取 PDF 文件并编码为 base64（模拟从接口接收 base64 内容）
    with open(file_path, "rb") as f:
        pdf_bytes = f.read()
    base64_str = base64.b64encode(pdf_bytes).decode("utf-8")
    print(f"已将 PDF 文件编码为 base64，长度: {len(base64_str)} 字符")

    # 方式 1: 使用 base64 字符串解析
    parser_content = PDFParser(enable_multimodal=False)
    docs = parser_content.parse_content(base64_str)
    print(f"base64 解析完成，内容长度: {len(docs[0].page_content)} 字符")

    # 方式 2: 使用原始字节解析
    docs2 = parser_content.parse_content(pdf_bytes)
    print(f"bytes 解析完成，内容长度: {len(docs2[0].page_content)} 字符")

    # 验证缓存：base64 和 bytes 指向同一内容，第二次应命中缓存
    print(f"\n两次解析结果一致: {docs[0].page_content == docs2[0].page_content}")

except FileNotFoundError:
    print(f"文件不存在: {file_path}")
except ValueError as e:
    print(f"内容解码失败: {e}")


# ==================== 示例 6: 直接调用 @tool 函数（无缓存） ====================
print("\n" + "=" * 60)
print("示例 6: 直接调用 @tool 函数（无缓存）")
print("=" * 60)

try:
    # 直接调用 @tool 函数 parse_pdf_from_file，配置从 settings 自动读取
    import os
    abs_path = os.path.abspath(file_path)
    text = parse_pdf_from_file.invoke({"file_path": abs_path})
    print(f"parse_pdf_from_file 解析完成，内容长度: {len(text)} 字符")

    # 直接调用 @tool 函数 parse_pdf_from_content
    with open(file_path, "rb") as f:
        pdf_bytes = f.read()
    base64_str = base64.b64encode(pdf_bytes).decode("utf-8")
    text2 = parse_pdf_from_content.invoke({"content": base64_str})
    print(f"parse_pdf_from_content 解析完成，内容长度: {len(text2)} 字符")

except FileNotFoundError:
    print(f"文件不存在: {file_path}")
except ValueError as e:
    print(f"内容解码失败: {e}")


# ==================== 示例 7: 使用自定义图像解析器 ====================
print("\n" + "=" * 60)
print("示例 7: 使用自定义图像解析器")
print("=" * 60)

from langchain_community.document_loaders.parsers import LLMImageBlobParser
from langchain_openai import ChatOpenAI

# 自定义图像解析器（示例）
# custom_parser = LLMImageBlobParser(
#     model=ChatOpenAI(
#         base_url="https://your-api.com/v1",
#         api_key="your-api-key",
#         model="your-vision-model"
#     )
# )
#
# parser_custom = PDFParser(
#     enable_multimodal=True,
#     custom_images_parser=custom_parser
# )

print("自定义图像解析器示例（已注释）")
print("取消注释代码并配置您的 API 密钥以使用")


print("\n" + "=" * 60)
print("所有示例演示完成！")
print("=" * 60)
