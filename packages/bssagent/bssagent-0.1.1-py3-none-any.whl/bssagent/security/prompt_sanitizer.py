import re
from typing import List

DANGEROUS_PATTERNS = [
    r"ignore\s*previous\s*instructions",
    r"system\s*[:=]\s*",
    r"<\s*\/*\s*script\s*\/*>",
    r"javascript:",
    r"data:text/html"
]

SENSITIVE_PATTERNS = [
    r"api[_-]?key",
    r"password",
    r"token",
    r"\b[A-Za-z0-9+/]{20,}={0,2}\b"  # base64-like strings
]

class PromptSanitizer:
    def __init__(self, input_max_length: int = 4000, dangerous_patterns: List[str] = DANGEROUS_PATTERNS, sensitive_patterns: List[str] = SENSITIVE_PATTERNS):
        self.dangerous_patterns = dangerous_patterns
        self.sensitive_patterns = sensitive_patterns
        self.input_max_length = input_max_length
    
    def sanitize_input(self, user_input: str) -> str:
        # Remove potential injection patterns
        for pattern in self.dangerous_patterns:
            user_input = re.sub(pattern, "", user_input, flags=re.IGNORECASE)
        
        # Limit input length
        if len(user_input) > self.input_max_length:
            raise ValueError("Input too long")
            
        return user_input.strip()
    

    """
    Validate the agent output to ensure it does not contain sensitive information
    e.g. api key, password, token, etc.
    code examples:
    ```python
    sanitizer = PromptSanitizer()
    if sanitizer.validate_agent_output(output):
        return output
    else:
        return "Error: Sensitive information detected"
    ```
    ```python
    sanitizer = PromptSanitizer()
    @app.post("/agent/chat")
    async def chat_with_agent(message: str):
        clean_message = sanitizer.sanitize_input(message)
        # Process with your LangGraph agent
        result = await process_agent(clean_message)
        
        if not sanitizer.validate_agent_output(result):
            raise HTTPException(status_code=400, detail="Output contains sensitive data")
        
        return {"response": result}
    ```
    """
    def validate_agent_output(self, output: str) -> bool:
        
        for pattern in self.sensitive_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                return False
        return True