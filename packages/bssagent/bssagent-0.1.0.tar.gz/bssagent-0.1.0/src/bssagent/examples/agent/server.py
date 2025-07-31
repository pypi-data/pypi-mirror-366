from fastapi import Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse
from bssagent.auth import AuthenticationWithKey
from bssagent.environment  import setup_environment_variables
from bssagent.infrastructure import AgentServer
import uuid
from bssagent.examples.agent import TestAgent

setup_environment_variables()
# enable_langsmith_tracing("agent-with-breakpoints")

agent = TestAgent(name="test_agent", description="A test agent")
# Create server with the agent
server = AgentServer(
    agent_instance=agent,
    use_rate_limiter=True,
    title="Breakpoint Agent Server",
    description="A server for the breakpoint agent with mathematical tools",
    version="1.0.0",
    host="0.0.0.0",
    port=8000
)

limiter = server.limiter
app = server.get_app()

auth = AuthenticationWithKey()

@app.post("/run_agent")
@limiter.limit("1/minute")
async def run_agent_endpoint(request: Request, user_id: str = Depends(auth)):
    try:
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized"}
            )
        
        data = await request.json()
        """ If the application is authenticated, user_id will be searched in the database"""
        # user_id = data.get("user_id") or str(uuid.uuid4())
        message = data.get("message", "Hello")
        
        if not user_id:
            return JSONResponse(
                status_code=400,
                content={"error": "user_id is required"}
            )
        
        # Get or create user session
        session = agent.get_or_create_user_session(user_id)
        
        # Create user-specific initial state
        initial_state = {
            "messages": [{"role": "user", "content": message}],
            "should_continue": False,
            "user_id": user_id
        }
        
        # Return streaming response
        return StreamingResponse(
            agent.stream(initial_state, session["thread"]),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )
        
    except Exception as e:
        server.logger.error(f"Error in run_agent: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# Add non-streaming run_agent endpoint for compatibility
async def run_agent_sync_endpoint(request: Request):
    """Synchronous version of run_agent for backward compatibility."""
    try:
        data = await request.json()
        user_id = data.get("user_id") or str(uuid.uuid4())
        message = data.get("message", "Hello")
        
        if not user_id:
            return JSONResponse(
                status_code=400,
                content={"error": "user_id is required"}
            )
        
        # Get or create user session
        session = agent.get_or_create_user_session(user_id)
        
        # Create user-specific initial state
        initial_state = {
            "messages": [{"role": "user", "content": message}],
            "should_continue": False,
            "user_id": user_id
        }
        
        # Run agent with user-specific thread (non-streaming)
        result = agent.invoke(initial_state, session["thread"])
        
        return {
            "result": result,
            "user_id": user_id,
            "thread_id": session["thread_id"]
        }
    except Exception as e:
        server.logger.error(f"Error in run_agent_sync: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# Add tool_call endpoint

async def tool_call_endpoint(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        session = agent.get_or_create_user_session(user_id)
        should_continue = data.get("should_continue", False)
        
        if not user_id:
            return JSONResponse(
                status_code=400,
                content={"error": "user_id is required"}
            )

        if should_continue:
            result = agent.continue_execution(session["thread"])
            return {"result": result}
        else:
            return {"result": "Agent execution paused"}
    except Exception as e:
        server.logger.error(f"Error in tool_call: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


if __name__ == "__main__":
    # Run the server
    server.run()

    