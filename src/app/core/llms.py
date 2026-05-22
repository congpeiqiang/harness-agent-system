"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import logging
from dotenv import load_dotenv
from langchain_core.language_models import ModelProfile

from app.core.config import settings
# 加载 .env 文件
load_dotenv()

# 导入配置模块

# 配置日志
logger = logging.getLogger(__name__)


def create_image_model():
    """
    创建图片处理模型（火山引擎 / 豆包视觉模型）
    
    使用环境变量中的 VISION_API_KEY 和 VISION_MODEL 配置
    """
    from langchain_openai import ChatOpenAI

    try:
        # 检查 API Key 是否配置
        if not settings.vision_api_key:
            logger.error("VISION_API_KEY 未设置，请在 .env 文件中配置")
            return None
        
        return ChatOpenAI(
            base_url=settings.vision_base_url,
            api_key=settings.vision_api_key,
            model=settings.vision_model,
        )
    except Exception as e:
        logger.error(f"创建图片模型失败: {e}")
        return None


def create_text_model():
    """
    创建文本处理模型（DeepSeek）
    
    使用环境变量中的 DEEPSEEK_API_KEY 和 DEEPSEEK_MODEL 配置
    """
    from langchain_deepseek import ChatDeepSeek
    
    try:
        # 检查 API Key 是否配置
        if not settings.deepseek_api_key:
            logger.error("DEEPSEEK_API_KEY 未设置，请在 .env 文件中配置")
            return None
        
        model = ChatDeepSeek(
            api_key=settings.deepseek_api_key,
            model=settings.deepseek_model,
            temperature=settings.ai.deepseek_temperature,
            base_url=settings.deepseek_base_url,
        )
        # 防止上下文超出token限制
        model.profile = ModelProfile(max_input_tokens=settings.ai.deepseek_max_input_tokens)
        return model
    except ImportError:
        logger.warning("langchain_deepseek 不可用")
        return None
    except Exception as e:
        logger.error(f"创建文本模型失败: {e}")
        return None


def create_vision_text_model():
    """
    创建火山引擎文本处理模型
    
    使用环境变量中的 VISION_API_KEY 和 VISION_TEXT_MODEL 配置
    """
    from langchain_openai import ChatOpenAI
    
    try:
        # 检查 API Key 是否配置
        if not settings.vision_api_key:
            logger.error("VISION_API_KEY 未设置，请在 .env 文件中配置")
            return None
        
        return ChatOpenAI(
            base_url=settings.vision_base_url,
            api_key=settings.vision_api_key,
            model=settings.vision_text_model,
        )
    except Exception as e:
        logger.error(f"创建火山引擎文本模型失败: {e}")
        return None


# 预创建的模型实例
image_llm_model = create_image_model()
deepseek_model = create_text_model()
vision_text_model = create_vision_text_model()
