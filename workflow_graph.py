from typing import TypedDict, Annotated, List
import operator
from langgraph.graph import StateGraph, END
from langgraph.checkpoint import MemorySaver

class WorkflowState(TypedDict):
    """工作流状态定义"""
    task_id: str
    user_input: str
    subtasks: List[dict]
    voc_result: dict
    geo_result: dict
    tiktok_result: dict
    price_result: dict
    final_report: str
    error: str
    current_step: str

def build_orchestration_graph(lead_agent, voc_agent, geo_agent, tiktok_agent, price_agent):
    """
    构建多Agent协作工作流 [citation:8]
    使用LangGraph实现状态管理和条件路由
    """
    
    workflow = StateGraph(WorkflowState)
    
    # 定义节点（Node = Agent任务）
    workflow.add_node("decompose_task", decompose_task_node(lead_agent))
    workflow.add_node("run_voc", run_agent_node(voc_agent))
    workflow.add_node("run_geo", run_agent_node(geo_agent))
    workflow.add_node("run_tiktok", run_agent_node(tiktok_agent))
    workflow.add_node("run_price", run_agent_node(price_agent))
    workflow.add_node("aggregate_results", aggregate_results_node(lead_agent))
    workflow.add_node("handle_error", error_handler_node())
    
    # 定义边（路由逻辑）
    workflow.set_entry_point("decompose_task")
    
    # 根据拆解出的子任务动态路由
    workflow.add_conditional_edges(
        "decompose_task",
        route_to_agents,
        {
            "voc": "run_voc",
            "geo": "run_geo",
            "tiktok": "run_tiktok",
            "price": "run_price",
            "error": "handle_error"
        }
    )
    
    # 所有子Agent完成后汇总
    workflow.add_edge("run_voc", "aggregate_results")
    workflow.add_edge("run_geo", "aggregate_results")
    workflow.add_edge("run_tiktok", "aggregate_results")
    workflow.add_edge("run_price", "aggregate_results")
    workflow.add_edge("aggregate_results", END)
    workflow.add_edge("handle_error", END)
    
    # 编译工作流（带持久化）
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app

def route_to_agents(state: WorkflowState):
    """根据任务类型路由到对应Agent"""
    subtask_types = [s.get("agent") for s in state.get("subtasks", [])]
    
    # 可以有多个路由
    return subtask_types[0] if subtask_types else "error"

def decompose_task_node(lead_agent):
    async def node(state: WorkflowState):
        context = AgentContext(
            task_id=state["task_id"],
            input_data={"user_message": state["user_input"]}
        )
        result = await lead_agent._parse_and_decompose(state["user_input"])
        return {"subtasks": result, "current_step": "decomposed"}
    return node

def aggregate_results_node(lead_agent):
    async def node(state: WorkflowState):
        # 汇总所有Agent结果
        all_results = {
            "voc": state.get("voc_result"),
            "geo": state.get("geo_result"),
            "tiktok": state.get("tiktok_result"),
            "price": state.get("price_result")
        }
        report = await lead_agent._aggregate_results(all_results)
        return {"final_report": report}
    return node

def error_handler_node():
    async def node(state: WorkflowState):
        print(f"[ERROR] Workflow failed at {state['current_step']}: {state.get('error')}")
        return {"final_report": f"执行失败：{state.get('error')}"}
    return node

def run_agent_node(agent):
    """通用Agent执行节点包装器"""
    async def node(state: WorkflowState):
        task = {"task": state["user_input"]}
        context = AgentContext(
            task_id=state["task_id"],
            input_data=task
        )
        result = await agent.execute(context)
        return {f"{agent.role}_result": result.output}
    return node
