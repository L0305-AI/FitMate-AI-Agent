from typing import Annotated, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool

from app.core.config import settings
from app.tools import all_tools
from app.rag.retriever import get_retriever_results
from app.agent.prompts import SYSTEM_PROMPT

# 1. 定义状态
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# 2. 初始化大模型
llm = ChatOpenAI(
    model=settings.LLM_MODEL,
    api_key=settings.LLM_API_KEY,
    base_url=settings.LLM_BASE_URL,
    temperature=0.7
)

# 3. 包装 RAG 工具
@tool
def search_knowledge_base(query: str) -> str:
    """当用户询问健身动作要领、营养学知识、伤病恢复建议时，使用此工具检索专业知识库。"""
    texts, _ = get_retriever_results(query)
    if not texts:
        return "知识库中没有找到相关内容。"
    return "\n\n".join(texts)

all_agent_tools = all_tools + [search_knowledge_base]
llm_with_tools = llm.bind_tools(all_agent_tools)

# 4. 定义节点
def call_model(state: AgentState):
    messages = state["messages"]
    
    # 如果第一条消息不是 SystemMessage，则在这里补上人设
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(all_agent_tools)

# 5. 路由
def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

# 6. 组装图
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
workflow.add_edge("tools", "agent")

fitmate_app = workflow.compile()