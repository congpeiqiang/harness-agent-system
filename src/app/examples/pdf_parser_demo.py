"""
PDF 解析器使用示例

演示专业 PDF 解析器的各种功能:
    1. 基础解析（仅文本）
    2. 多模态解析（包含图像识别）
    3. 缓存机制演示
    4. 解析后获取纯文本
    5. 通过 base64 内容解析
    6. 直接调用 @tool 函数（无缓存）
    7. 通过在线 URL 直接解析
    8. 使用自定义图像解析器

使用方法:
    方式1 - 直接修改代码中的 RUN_EXAMPLES 变量：
        RUN_EXAMPLES = []           # 运行所有示例
        RUN_EXAMPLES = [1]          # 只运行示例 1
        RUN_EXAMPLES = [1, 3, 5]    # 运行示例 1、3、5
    
    方式2 - 命令行参数（可选）：
        python pdf_parser_demo.py --list       # 列出所有示例
        python pdf_parser_demo.py 1            # 只运行示例 1
        python pdf_parser_demo.py 1 3 5        # 运行示例 1、3、5
"""

# ============================================================
# 配置区：在这里指定要运行的示例
# ============================================================
# 可选值：
#   []              - 运行所有示例（默认）
#   [1]             - 只运行示例 1
#   [1, 3, 5]       - 运行示例 1、3、5
#   [7, 8]          - 运行示例 7 和 8
# ============================================================
RUN_EXAMPLES: list[int] = [7]
# ============================================================

import argparse
import base64
import logging
import sys

# 配置日志级别
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from app.processors.pdf_parser import PDFParser


# ==================== 示例定义 ====================
EXAMPLES = {
    1: ("基础解析（仅文本）", "demo_basic"),
    2: ("多模态解析（包含图像识别）", "demo_multimodal"),
    3: ("缓存管理", "demo_cache"),
    4: ("解析后获取纯文本", "demo_extract_text"),
    5: ("通过 base64 内容解析", "demo_base64"),
    6: ("直接调用 @tool 函数（无缓存）", "demo_tool"),
    7: ("通过在线 URL 直接解析", "demo_url"),
    8: ("使用自定义图像解析器", "demo_custom_parser"),
}


def print_example_list():
    """打印所有示例列表"""
    print("可用示例列表:")
    print("-" * 50)
    for num, (name, _) in EXAMPLES.items():
        print(f"  {num}. {name}")
    print("-" * 50)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="PDF 解析器使用示例",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python pdf_parser_demo.py              # 运行所有示例
  python pdf_parser_demo.py 1            # 只运行示例 1
  python pdf_parser_demo.py 1 3 5        # 运行示例 1、3、5
  python pdf_parser_demo.py --list       # 列出所有示例
        """
    )
    parser.add_argument(
        "examples",
        nargs="*",
        type=int,
        help="要运行的示例编号（可选，默认为所有示例）",
        metavar="N"
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="列出所有可用示例"
    )
    return parser.parse_args()


# ==================== 示例 1: 基础解析（仅文本） ====================
def demo_basic():
    print("=" * 60)
    print("示例 1: 基础解析（仅文本）")
    print("=" * 60)

    parser_basic = PDFParser(
        mode="single",
        table_strategy="lines",
        enable_multimodal=False  # 关闭多模态
    )

    file_path = "../resources/旅行日记.pdf"

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
def demo_multimodal():
    print("\n" + "=" * 60)
    print("示例 2: 多模态解析（包含图像识别）")
    print("=" * 60)

    parser_multimodal = PDFParser(
        mode="single",
        table_strategy="lines",
        enable_multimodal=True,  # 开启多模态
        extract_images=True
    )

    file_path = "../resources/旅行日记.pdf"

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
def demo_cache():
    print("\n" + "=" * 60)
    print("示例 3: 缓存管理")
    print("=" * 60)

    parser_basic = PDFParser(
        mode="single",
        table_strategy="lines",
        enable_multimodal=False
    )

    # 清除所有缓存
    print("\n清除所有缓存...")
    parser_basic.clear_cache()
    print("缓存已清除")


# ==================== 示例 4: 解析后获取纯文本 ====================
def demo_extract_text():
    print("\n" + "=" * 60)
    print("示例 4: 解析后获取纯文本")
    print("=" * 60)

    file_path = "../resources/旅行日记.pdf"

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
def demo_base64():
    print("\n" + "=" * 60)
    print("示例 5: 通过 base64 内容解析")
    print("=" * 60)

    file_path = "../resources/旅行日记.pdf"

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
def demo_tool():
    print("\n" + "=" * 60)
    print("示例 6: 直接调用 @tool 函数（无缓存）")
    print("=" * 60)

    file_path = "../resources/旅行日记.pdf"

    try:
        from app.tools.pdf_parse_tool import parse_pdf_from_file, parse_pdf_from_content

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


# ==================== 示例 7: 通过在线 URL 直接解析 ====================
def demo_url():
    print("\n" + "=" * 60)
    print("示例 7: 通过在线 URL 直接解析（无需先下载）")
    print("=" * 60)

    from app.tools.pdf_parse_tool import parse_pdf_from_url

    # 使用公开的 PDF URL 进行测试（可替换为任意有效 PDF URL）
    test_url = "https://patentimages.storage.googleapis.com/aa/80/e5/7ef9a628254e36/CN1406291A.pdf"

    parser_url = PDFParser(enable_multimodal=False)

    try:
        print(f"\n直接解析在线 PDF: {test_url}")
        docs = parser_url.parse_url(test_url)
        print(f"解析完成，文档片段数: {len(docs)}")
        if docs:
            print(f"第一片段内容预览 (前 300 字符):")
            print("-" * 40)
            print(docs[0].page_content[:300])
            print("-" * 40)

        # 再次解析，验证缓存命中
        print("\n第二次解析（应命中缓存）...")
        docs_cached = parser_url.parse_url(test_url)
        print(f"缓存解析完成，文档片段数: {len(docs_cached)}")

        # 使用 Tool 函数解析
        print("\n使用 parse_pdf_from_url Tool 解析...")
        text = parse_pdf_from_url.invoke({"url": test_url})
        print(f"Tool 解析完成，文本长度: {len(text)} 字符")
        print(f"内容预览 (前 300 字符):")
        print("-" * 40)
        print(text[:300])
        print("-" * 40)

    except Exception as e:
        print(f"URL 解析失败: {e}")
        print("请检查网络连接或替换为其他有效的 PDF URL")


# ==================== 示例 8: 使用自定义图像解析器 ====================
def demo_custom_parser():
    print("\n" + "=" * 60)
    print("示例 8: 使用自定义图像解析器")
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


# ==================== 主程序 ====================
def run_all_examples():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("运行所有示例")
    print("=" * 60)
    
    for num in sorted(EXAMPLES.keys()):
        func_name = EXAMPLES[num][1]
        func = globals()[func_name]
        try:
            func()
        except Exception as e:
            print(f"\n示例 {num} 执行失败: {e}")


def run_examples(example_numbers):
    """运行指定的示例"""
    invalid = [n for n in example_numbers if n not in EXAMPLES]
    if invalid:
        print(f"无效的示例编号: {invalid}")
        print(f"可用示例编号: {list(EXAMPLES.keys())}")
        return False
    
    for num in sorted(set(example_numbers)):
        func_name = EXAMPLES[num][1]
        func = globals()[func_name]
        try:
            func()
        except Exception as e:
            print(f"\n示例 {num} 执行失败: {e}")
    return True


def main():
    # 优先使用代码中定义的 RUN_EXAMPLES 变量
    # 如果 RUN_EXAMPLES 为空列表，则尝试从命令行参数获取
    if RUN_EXAMPLES:
        print(f"使用代码中配置的示例编号: {RUN_EXAMPLES}")
        if not run_examples(RUN_EXAMPLES):
            sys.exit(1)
    else:
        # 从命令行参数解析
        args = parse_args()
        
        if args.list:
            print_example_list()
            return
        
        if not args.examples:
            # 没有指定示例编号，运行所有示例
            run_all_examples()
        else:
            # 运行指定的示例
            if not run_examples(args.examples):
                sys.exit(1)
    
    print("\n" + "=" * 60)
    print("示例演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
