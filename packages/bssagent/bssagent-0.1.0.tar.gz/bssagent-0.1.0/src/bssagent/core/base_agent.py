import asyncio
import json
from typing import Any, AsyncGenerator, Dict, Optional
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import StreamMode
from .agent_session import AgentSessionManager


class BaseAgent:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.session_manager = AgentSessionManager()
        self.compiled_graph: Optional[CompiledStateGraph] = None
        self.define_graph()
    
    # Session management methods - delegate to session manager
    def create_user_session(self, user_id: str) -> Dict[str, Any]:
        """Create a new session for a user and save it to the database."""
        return self.session_manager.create_user_session(user_id)
    
    def get_or_create_user_session(self, user_id: str) -> Dict[str, Any]:
        """Get existing session or create new one for user."""
        return self.session_manager.get_or_create_user_session(user_id)
    
    def get_user_session(self, user_id: str) -> Dict[str, Any]:
        """Get a user session from memory or database."""
        return self.session_manager.get_user_session(user_id)
    
    def update_session(self, user_id: str, updates: Dict[str, Any]):
        """Update session data and save to database."""
        self.session_manager.update_session(user_id, updates)
    
    def deactivate_session(self, user_id: str):
        """Deactivate a user session."""
        self.session_manager.deactivate_session(user_id)
    
    def get_user_session_thread(self, user_id: str) -> Dict[str, Any]:
        """Get a user session thread."""
        return self.session_manager.get_user_session_thread(user_id)
    
    def get_user_session_thread_id(self, user_id: str) -> str:
        """Get a user session thread id."""
        return self.session_manager.get_user_session_thread_id(user_id)
    
    def get_user_session_user_id(self, user_id: str) -> str:
        """Get a user session user id."""
        return self.session_manager.get_user_session_user_id(user_id)
    
    def list_active_sessions(self) -> list:
        """List all active sessions from database."""
        return self.session_manager.list_active_sessions()
    
    # Additional session management methods
    def clear_session_cache(self):
        """Clear the in-memory session cache."""
        self.session_manager.clear_memory_cache()
    
    def get_session_count(self) -> int:
        """Get the number of sessions in memory cache."""
        return self.session_manager.get_session_count()
    
    def has_session(self, user_id: str) -> bool:
        """Check if a user has an active session in memory."""
        return self.session_manager.has_session(user_id)

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