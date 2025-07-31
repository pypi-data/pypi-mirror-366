from langgraph.graph import MessagesState
# Define the state for the agent
class State(MessagesState):
    result: int
    should_continue: bool
    user_id: str