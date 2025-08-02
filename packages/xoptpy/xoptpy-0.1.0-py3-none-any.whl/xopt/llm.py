import litellm
from typing import Optional, Any


def call_llm(prompt: str, model: str = "ollama/llama3.2:3b", trace_instance=None, **kwargs) -> str:
    """Call any LLM via LiteLLM - supports Ollama, OpenAI, Claude, Gemini, etc.
    
    Args:
        prompt: The input prompt/message
        model: Model identifier (e.g. "ollama/llama3.2:3b", "gpt-4", "claude-3-sonnet-20240229")
        trace_instance: Optional trace instance for logging
        **kwargs: Additional parameters passed to litellm.completion
        
    Returns:
        LLM response as string
        
    Examples:
        # Local Ollama
        call_llm("Hello", "ollama/llama3.2:3b")
        
        # OpenAI (needs OPENAI_API_KEY env var)
        call_llm("Hello", "gpt-4")
        
        # Claude (needs ANTHROPIC_API_KEY env var)
        call_llm("Hello", "claude-3-sonnet-20240229")
        
        # Gemini (needs GEMINI_API_KEY env var)
        call_llm("Hello", "gemini-pro")
    """
    
    # Log the LLM call if trace instance is available
    if trace_instance:
        trace_instance.log_trace_event("llm_call", {
            "model": model,
            "prompt": prompt,
            "prompt_length": len(prompt)
        })
    
    try:
        # Set default parameters
        params = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.1),
            "max_tokens": kwargs.get("max_tokens", 500)
        }
        
        # Add any additional kwargs
        for key, value in kwargs.items():
            if key not in ["temperature", "max_tokens"]:
                params[key] = value
        
        response = litellm.completion(**params)
        llm_response = response.choices[0].message.content.strip()
        
        # Log the LLM response
        if trace_instance:
            trace_instance.log_trace_event("llm_call", {
                "response": llm_response,
                "response_length": len(llm_response),
                "status": "success"
            })
        
        return llm_response
        
    except Exception as e:
        error_msg = f"LLM call failed: {str(e)}"
        
        if trace_instance:
            trace_instance.log_trace_event("llm_call", {
                "error": error_msg
            })
        
        return f"Error: {error_msg}"