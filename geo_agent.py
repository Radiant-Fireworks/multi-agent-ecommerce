from typing import Dict, Any
import json
from .base_agent import BaseAgent, AgentContext, AgentResult

class GEOAgent(BaseAgent):
    """
    GEO内容优化师 - AI友好内容创作 [citation:1]
    核心原则：关键词堆砌禁止，采用"定量数据+权威引用"策略
    """
    
    async def execute(self, context: AgentContext) -> AgentResult:
        task = context.input_data.get("task", "")
        
        # 1. 提取内容需求
        content_req = await self._extract_requirements(task)
        
        # 2. 生成GEO优化文案
        articles = await self._generate_geo_content(content_req)
        
        # 3. 补充数据引用和SEO元素
        enriched = await self._enrich_with_data(articles)
        
        return AgentResult(
            success=True,
            output={
                "blog_article": enriched.get("blog"),
                "product_description": enriched.get("product_page"),
                "meta_tags": enriched.get("meta"),
                "keywords": content_req.get("keywords", [])
            }
        )
    
    async def _generate_geo_content(self, req: Dict) -> Dict:
        """生成GEO优化文案 - 适配AI搜索引擎 [citation:1]"""
        system_prompt = """
        你是GEO（Generative Engine Optimization）内容优化师。
        
        写作标准：
        1. 禁止关键词堆砌，用自然语言覆盖语义
        2. 必须包含3个以上具体数据（如"承重450磅""收纳后20×15cm"）
        3. 至少引用1个权威来源（如"户外装备实验室测试""ASTM标准"）
        4. 风格：专业+易懂，避免口语化
        
        面向读者：AI搜索引擎（ChatGPT、Perplexity、Gemini）和真实用户
        """
        
        prompt = f"""
        产品需求：{json.dumps(req, ensure_ascii=False)}
        
        请生成：
        1. 独立站博客文章（标题+H2子标题+正文+CTA按钮文案）
        2. 产品详情页核心卖点（3-5个AI友好段落）
        """
        
        response = await self.call_llm(prompt, system_prompt)
        
        # 解析响应，分离博客和产品页内容
        return {
            "blog": response,
            "product_page": response,  # 实际需精细解析
            "meta": {"title": req.get("product_name", "") + "专业评测"}
        }
    
    async def _enrich_with_data(self, content: Dict) -> Dict:
        """补充定量数据和权威引用"""
        # 自动注入产品规格数据
        # 实际应从数据库获取真实参数
        return content
