import asyncio
from dotenv import load_dotenv
from agents.lead_agent import LeadAgent
from agents.voc_agent import VOCAgent
from agents.geo_agent import GEOAgent
from agents.tiktok_agent import TikTokAgent  # 需实现
from agents.price_monitor_agent import PriceMonitorAgent
from orchestration.workflow_graph import build_orchestration_graph

load_dotenv()

async def main():
    """主入口 - 启动多Agent系统"""
    
    # 1. 加载配置（从YAML/环境变量）
    agent_config = {
        "lead": {"model": "qwen-max", "allowed_agents": ["voc", "geo", "tiktok", "price_monitor"]},
        "voc": {"model": "qwen-turbo", "provider": "qwen"},
        "geo": {"model": "qwen-max", "provider": "qwen"},
        "tiktok": {"model": "qwen-turbo", "provider": "qwen"},
        "price_monitor": {"model": "qwen-turbo", "provider": "qwen"}
    }
    
    # 2. 实例化所有Agent
    lead = LeadAgent(agent_config["lead"])
    voc = VOCAgent(agent_config["voc"])
    geo = GEOAgent(agent_config["geo"])
    tiktok = TikTokAgent(agent_config["tiktok"])
    price = PriceMonitorAgent(agent_config["price_monitor"])
    
    # 3. 注册子Agent到大总管
    lead.register_sub_agent("voc", voc)
    lead.register_sub_agent("geo", geo)
    lead.register_sub_agent("tiktok", tiktok)
    lead.register_sub_agent("price_monitor", price)
    
    # 4. 构建LangGraph工作流
    workflow = build_orchestration_graph(lead, voc, geo, tiktok, price)
    
    # 5. 启动交互式任务处理
    print("🤖 多Agent电商运营系统已启动")
    print("使用示例：")
    print("  - '帮我分析露营折叠床的竞品，并生成推广文案'")
    print("  - '监控竞品价格，发现异常告警'")
    print()
    
    while True:
        user_input = input("\n👤 用户: ")
        if user_input.lower() in ["exit", "quit", "退出"]:
            break
        
        # 执行工作流
        initial_state = {
            "task_id": f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "user_input": user_input,
            "subtasks": [],
            "voc_result": {},
            "geo_result": {},
            "tiktok_result": {},
            "price_result": {},
            "final_report": "",
            "error": "",
            "current_step": "start"
        }
        
        # 运行异步工作流
        result = await workflow.ainvoke(initial_state)
        
        print(f"\n📋 执行报告:\n{result.get('final_report', '无输出')}")

if __name__ == "__main__":
    asyncio.run(main())
