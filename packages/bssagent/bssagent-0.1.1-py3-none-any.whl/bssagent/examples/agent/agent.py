
# Define a langraph react agent with tools above
from typing import Type
from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from bssagent.core.base_agent import BaseAgent
from .tools import tools
from .state import State

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

llm_with_tools = llm.bind_tools(tools)

# Define a system message
sys_msg = SystemMessage(content="You are a helpful assistant. You can add, subtract, multiply, and divide numbers. You can also break the flow of the conversation by saying 'break'.")

def should_continue(state: State):
    return {"should_continue": state["should_continue"]}

# First node
def assistant_node(state: State):
    # Get user-specific system message
    sys_msg = get_system_message(state.get("user_id"))
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

def get_system_message(user_id: str = "") -> SystemMessage:
    base_content = "You are a helpful assistant..."
    if user_id:
        base_content += f" You are assisting user {user_id}."
    return SystemMessage(content=base_content)

class TestAgent(BaseAgent):
    def define_graph(self):
        graph = StateGraph(State)
        graph.add_node("assistant", assistant_node)
        graph.add_node("tools", ToolNode(tools))

        graph.add_edge(START, "assistant")
        graph.add_edge("assistant", "tools")
        graph.add_conditional_edges("assistant", tools_condition)
        memory = MemorySaver()
        # self.compiled_graph = graph.compile(checkpointer=memory, interrupt_before=["tools"])
        self.compiled_graph = graph.compile()