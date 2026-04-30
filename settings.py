import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # LLM配置
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "qwen")  # qwen/openai/anthropic
    QWEN_API_KEY = os.getenv("QWEN_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # 模型分级配置 [citation:1]
    MODEL_STRATEGIC = "qwen-max"      # 决策层使用
    MODEL_EXECUTION = "qwen-turbo"    # 执行层使用
    
    # 通信配置
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    FEISHU_APP_ID = os.getenv("FEISHU_APP_ID")
    FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET")
    
    # 工具配置
    COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY")  # MCP工具路由 [citation:10]
    AGORIO_API_KEY = os.getenv("AGORIO_API_KEY")      # 电商协议SDK [citation:4]
    
    # 电商平台
    AMAZON_API_KEY = os.getenv("AMAZON_API_KEY")
    SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")
    
    # Agent配置
    MAX_ITERATIONS = 20
    TASK_TIMEOUT = 300  # 5分钟
    MEMORY_TTL = 86400  # 24小时

settings = Settings()
