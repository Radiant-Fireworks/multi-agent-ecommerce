from typing import Dict, Any, List
import json
from .base_agent import BaseAgent, AgentContext, AgentResult

class VOCAgent(BaseAgent):
    """
    VOC市场分析师 - 竞品评价分析、用户痛点挖掘 [citation:1]
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("VOC分析师", "analyst", config)
    
    async def execute(self, context: AgentContext) -> AgentResult:
        task = context.input_data.get("task", "")
        
        # 1. 提取目标产品/竞品信息
        target = await self._extract_target(task)
        
        # 2. 抓取竞品评价（亚马逊/速卖通）
        reviews = await self._fetch_reviews(target)
        
        # 3. 分析用户痛点
        pain_points = await self._analyze_pain_points(reviews)
        
        # 4. 生成竞品SWOT分析
        swot = await self._generate_swot(reviews, target)
        
        return AgentResult(
            success=True,
            output={
                "target": target,
                "pain_points": pain_points,
                "swot_analysis": swot,
                "sample_reviews": reviews[:10]
            }
        )
    
    async def _extract_target(self, task: str) -> Dict:
        """从任务中提取目标产品信息"""
        prompt = f"""
        从以下任务中提取需要分析的竞品/产品信息：
        任务：{task}
        
        输出JSON格式：{{"product_name": "", "category": "", "competitors": []}}
        """
        response = await self.call_llm(prompt)
        return json.loads(response)
    
    async def _fetch_reviews(self, target: Dict) -> List[Dict]:
        """抓取竞品评价（模拟实现）"""
        # 实际使用：亚马逊Product Advertising API / 爬虫
        return [
            {"rating": 2, "content": "承重不足，用了两周就变形了", "platform": "amazon"},
            {"rating": 3, "content": "收纳很不方便，折叠后占地方", "platform": "amazon"},
            {"rating": 4, "content": "价格合适但质量一般", "platform": "aliexpress"},
        ]
    
    async def _analyze_pain_points(self, reviews: List[Dict]) -> List[Dict]:
        """分析用户核心痛点 [citation:1]"""
        reviews_text = "\n".join([r["content"] for r in reviews])
        prompt = f"""
        分析以下用户评价，提炼核心痛点：
        
        评价：{reviews_text}
        
        输出格式：
        [
            {{"pain_point": "痛点描述", "frequency": "高频/中频/低频", "examples": ["示例引用"]}}
        ]
        """
        response = await self.call_llm(prompt)
        return json.loads(response)
    
    async def _generate_swot(self, reviews: List[Dict], target: Dict) -> Dict:
        """生成SWOT分析矩阵"""
        prompt = f"""
        基于以下用户评价，对产品 {target.get('product_name')} 进行SWOT分析：
        
        评价数据：{reviews[:20]}
        
        输出JSON：{{"strengths": [], "weaknesses": [], "opportunities": [], "threats": []}}
        """
        response = await self.call_llm(prompt)
        return json.loads(response)
