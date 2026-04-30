from typing import Dict, Any, List
from datetime import datetime, timedelta
import json
from .base_agent import BaseAgent, AgentContext, AgentResult

class LeadAgent(BaseAgent):
    """
    大总管Agent - 负责任务拆解、分发、汇总 [citation:1]
    核心纪律：绝不越权执行其他Agent的工作
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("大总管", "orchestrator", config)
        self.allowed_agents = config.get("allowed_agents", [])
        self.sub_agents = {}  # 子Agent实例注册
        
    def register_sub_agent(self, name: str, agent: BaseAgent):
        """注册子Agent"""
        self.sub_agents[name] = agent
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """接收用户指令并协调执行"""
        try:
            user_input = context.input_data.get("user_message", "")
            
            # 1. 解析用户意图并拆解任务 [citation:9]
            subtasks = await self._parse_and_decompose(user_input)
            
            # 2. 分发任务给各子Agent
            results = await self._dispatch_tasks(subtasks, context.task_id)
            
            # 3. 汇总结果，生成报告
            summary = await self._aggregate_results(results)
            
            # 4. 通知用户（飞书/callback）
            await self._notify_user(summary, context)
            
            return AgentResult(
                success=True,
                output={"summary": summary, "details": results},
                metrics={"subtasks_count": len(subtasks)}
            )
        except Exception as e:
            # 异常处理：1分钟内同步用户 [citation:1]
            await self._notify_error(str(e), context)
            return AgentResult(success=False, output={}, error=str(e))
    
    async def _parse_and_decompose(self, user_input: str) -> List[Dict]:
        """将用户输入拆解为可执行的子任务"""
        system_prompt = """
        你是跨境电商团队的"大总管"。
        你的职责是：将用户的运营需求拆解为具体子任务，分发给专业Agent执行。
        
        可用Agent及其职能：
        - voc: VOC市场分析师 - 竞品评价分析、用户痛点挖掘
        - geo: GEO内容优化师 - AI友好文案创作、SEO优化
        - tiktok: TikTok编导 - 爆款脚本生成、视频创意
        - price_monitor: 价格监控专家 - 竞品价格追踪、异常告警
        
        输出格式（JSON数组）：
        [{"agent": "agent_name", "task": "具体任务描述", "deadline_minutes": 30}]
        """
        
        prompt = f"用户需求：{user_input}\n请拆解任务并分配Agent。"
        
        response = await self.call_llm(prompt, system_prompt)
        # 解析JSON响应
        return json.loads(response)
    
    async def _dispatch_tasks(self, subtasks: List[Dict], parent_task_id: str) -> Dict:
        """并行分发任务给各Agent"""
        results = {}
        tasks = []
        
        for subtask in subtasks:
            agent_name = subtask["agent"]
            if agent_name in self.sub_agents:
                # 创建子任务上下文
                sub_context = AgentContext(
                    task_id=f"{parent_task_id}_{agent_name}",
                    parent_task_id=parent_task_id,
                    input_data={"task": subtask["task"]},
                    deadline=datetime.now() + timedelta(minutes=subtask.get("deadline_minutes", 60))
                )
                
                # 异步执行子任务
                task = asyncio.create_task(
                    self.sub_agents[agent_name].execute(sub_context)
                )
                tasks.append((agent_name, task))
        
        # 等待所有子任务完成（带超时控制）
        for agent_name, task in tasks:
            try:
                result = await asyncio.wait_for(task, timeout=300)
                results[agent_name] = result.output
            except asyncio.TimeoutError:
                results[agent_name] = {"error": f"{agent_name}执行超时"}
                
        return results
    
    async def _aggregate_results(self, results: Dict) -> str:
        """汇总各Agent结果生成结构化报告"""
        prompt = f"""
        请汇总以下各Agent的工作成果，生成一份简洁的运营报告：
        
        {json.dumps(results, ensure_ascii=False, indent=2)}
        
        报告要求：
        1. 总体执行情况
        2. 各模块关键输出摘要
        3. 下一步建议（如有）
        """
        
        return await self.call_llm(prompt)
    
    async def _notify_user(self, summary: str, context: AgentContext):
        """通过飞书通知用户 [citation:1]"""
        # 集成飞书Webhook
        webhook_url = context.input_data.get("webhook_url")
        if webhook_url:
            # 发送飞书卡片消息
            pass
        print(f"[大总管] 任务完成：{summary[:200]}")
    
    async def _notify_error(self, error: str, context: AgentContext):
        """异常1分钟内同步用户"""
        print(f"[大总管] 异常告警：{error}")
        # 发送告警通知
