import asyncio
import json
from typing import AsyncGenerator, Optional
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import StreamMode


class BaseAgent:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.compiled_graph: Optional[CompiledStateGraph] = None
        self.define_graph()

    def get_name(self) -> str:
        return self.name
        
    def set_compiled_graph(self, compiled_graph: CompiledStateGraph):
        self.compiled_graph = compiled_graph

    def invoke(self, state, thread):
        """Run the agent with initial state."""
        if self.compiled_graph is None:
            raise ValueError("Compiled graph is not set")
        return self.compiled_graph.invoke(state, thread)

    async def stream(self, state, thread, stream_mode: StreamMode = "values") -> AsyncGenerator[str, None]:
        """Stream the agent with initial state."""
        if self.compiled_graph is None:
            raise ValueError("Compiled graph is not set")
        try:
            # Use stream method instead of invoke
            # Work only if stream_mode is values
            # Need to improve this to work with other stream_modes (tasks, updates, checkpoints, messages, etc.)
            for event in self.compiled_graph.stream(state, thread, stream_mode=stream_mode):
                # Check if the event includes input attribute
                last_message = event["messages"][-1]
                json_message = last_message.json()
                print(json_message)
                chunk_data = {
                    "status": "processing",
                    "content": last_message.content,
                    "timestamp": asyncio.get_event_loop().time(),
                    "message_type": last_message.type,
                    "message_name": last_message.name  
                }
                
                yield f"data: {json.dumps(chunk_data)}\n\n"
            
            # Send completion signal
            completion_data = {
                "status": "complete",
                "timestamp": asyncio.get_event_loop().time()
            }
            yield f"data: {json.dumps(completion_data)}\n\n"
            
        except Exception as e:
            # Send error signal
            error_data = {
                "status": "error",
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    def get_state(self, thread):
        """Get current state from the graph."""
        if self.compiled_graph is None:
            raise ValueError("Compiled graph is not set")
        return self.compiled_graph.get_state(thread)
    
    def continue_execution(self, thread):
        """Continue execution from current state."""
        if self.compiled_graph is None:
            raise ValueError("Compiled graph is not set")
        return self.compiled_graph.invoke(None, thread)
    
    def define_graph(self):
        """Define the graph for the agent."""
        pass