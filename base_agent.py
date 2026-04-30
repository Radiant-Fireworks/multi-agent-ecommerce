from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json
import asyncio
from openai import AsyncOpenAI
from dashscope import Generation
import dashscope

@dataclass
class AgentContext:
    """Agent执行上下文"""
    task_id: str
    parent_task_id: Optional[str] = None
    input_data: Dict[str, Any] = field(default_factory=dict)
    memory: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None

@dataclass
class AgentResult:
    """Agent执行结果"""
    success: bool
    output: Dict[str, Any]
    error: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)

class BaseAgent(ABC):
    """Agent基类 - 所有角色的基础"""
    
    def __init__(self, name: str, role: str, config: Dict[str, Any]):
        self.name = name
        self.role = role
        self.config = config
        self.model = config.get("model", "qwen-max")
        
        # 初始化LLM客户端
        if config.get("provider") == "openai":
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            dashscope.api_key = settings.QWEN_API_KEY
            
        # 消息队列（用于异步通信）
        self.message_queue = None  # Redis连接占位
    
    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """每个Agent实现自己的执行逻辑"""
        pass
    
    async def call_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """调用大模型API"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        if self.config.get("provider") == "openai":
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        else:
            # 阿里云千问API [citation:1]
            response = Generation.call(
                model=self.model,
                messages=messages,
                result_format='message'
            )
            return response.output.choices[0].message.content
    
    async def send_message(self, target_agent: str, message: Dict[str, Any]):
        """发送消息给其他Agent"""
        # Redis Pub/Sub 实现 [citation:6]
        await self.message_queue.publish(
            f"agent:{target_agent}",
            json.dumps({
                "from": self.name,
                "to": target_agent,
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
        )
    
    async def use_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具（通过Composio MCP）[citation:10]"""
        # 集成Composio SDK
        pass
