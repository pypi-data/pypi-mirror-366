from .models import Module, StepResult
from .client import client
from typing import Dict, Any
import json
from datetime import datetime
import uuid


class ModuleInstance:
    """Running instance of a module"""
    
    def __init__(self, module: Module, config: Dict[str, Any]):
        self.module = module
        self.config = config
        self.module_calls = []  # Track module calls made during execution
        self.trace_id = str(uuid.uuid4())
        self.trace_file = f"trace_{self.trace_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.trace_data = {
            "trace_id": self.trace_id,
            "module_name": self.module.name,
            "start_time": datetime.now().isoformat(),
            "steps": [],
            "llm_calls": [],
            "module_calls": []
        }
        
    def log_trace_event(self, event_type: str, data: Dict[str, Any]):
        """Log an event to the trace"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data
        }
        
        if event_type == "step":
            self.trace_data["steps"].append(event)
        elif event_type == "llm_call":
            self.trace_data["llm_calls"].append(event)
        elif event_type == "module_call":
            self.trace_data["module_calls"].append(event)
    
    def save_trace(self):
        """Save trace to file"""
        self.trace_data["end_time"] = datetime.now().isoformat()
        try:
            with open(self.trace_file, 'w') as f:
                json.dump(self.trace_data, f, indent=2)
            print(f"📊 Trace saved to: {self.trace_file}")
        except Exception as e:
            print(f"❌ Failed to save trace: {e}")

    def call(self, input_data: Any) -> Any:
        """Execute the module with input data"""
        self.module_calls = []  # Reset module calls for this execution
        
        # Log the initial input
        self.log_trace_event("step", {
            "step_name": "module_call",
            "input": str(input_data),
            "module": self.module.name
        })
        
        if self.module.start_step and self.module.start_step in self.module.steps:
            step_info = self.module.steps[self.module.start_step]
            
            # Log step execution
            self.log_trace_event("step", {
                "step_name": self.module.start_step,
                "input": str(input_data),
                "module": self.module.name
            })
            
            # Set current trace instance for step functions that need it via globals
            import sys
            step_module_name = step_info['function'].__module__
            if step_module_name in sys.modules:
                step_module = sys.modules[step_module_name]
                if hasattr(step_module, '_current_trace_instance'):
                    old_trace = getattr(step_module, '_current_trace_instance', None)
                    setattr(step_module, '_current_trace_instance', self)
                else:
                    old_trace = None
            else:
                old_trace = None
            
            result = step_info['function'](input_data)
            
            # Restore old trace instance
            if step_module_name in sys.modules and old_trace is not None:
                step_module = sys.modules[step_module_name]
                if hasattr(step_module, '_current_trace_instance'):
                    setattr(step_module, '_current_trace_instance', old_trace)
            
            # Log step result
            self.log_trace_event("step", {
                "step_name": f"{self.module.start_step}_result",
                "output": str(result.content) if hasattr(result, 'content') else str(result),
                "action": result.action if hasattr(result, 'action') else None
            })
            
            # Process step results in a loop to handle step_call chains and module_call chains
            max_iterations = 5  # Prevent infinite loops
            iteration_count = 0
            while hasattr(result, 'action') and result.action in ["step_call", "module_call"] and iteration_count < max_iterations:
                iteration_count += 1
                
                if result.action == "step_call":
                    # Handle internal step call
                    step_name = result.module_name  # Actually contains step name
                    step_input = result.module_input
                    
                    if step_name in self.module.steps:
                        step_info = self.module.steps[step_name]
                        
                        # Log step execution
                        self.log_trace_event("step", {
                            "step_name": step_name,
                            "input": str(step_input),
                            "module": self.module.name
                        })
                        
                        # Set current trace instance for step functions that need it via globals
                        import sys
                        step_module_name = step_info['function'].__module__
                        if step_module_name in sys.modules:
                            step_module = sys.modules[step_module_name]
                            if hasattr(step_module, '_current_trace_instance'):
                                old_trace = getattr(step_module, '_current_trace_instance', None)
                                setattr(step_module, '_current_trace_instance', self)
                            else:
                                old_trace = None
                        else:
                            old_trace = None
                        
                        step_result = step_info['function'](step_input)
                        
                        # Restore old trace instance
                        if step_module_name in sys.modules and old_trace is not None:
                            step_module = sys.modules[step_module_name]
                            if hasattr(step_module, '_current_trace_instance'):
                                setattr(step_module, '_current_trace_instance', old_trace)
                        
                        # Log step result and continue processing
                        self.log_trace_event("step", {
                            "step_name": f"{step_name}_result",
                            "output": str(step_result.content) if hasattr(step_result, 'content') else str(step_result),
                            "action": step_result.action if hasattr(step_result, 'action') else None
                        })
                        
                        # Recursively handle the step result
                        result = step_result
                    else:
                        error_msg = f"Step '{step_name}' not found in module {self.module.name}"
                        self.log_trace_event("step", {
                            "step_name": "error",
                            "error": error_msg
                        })
                        self.save_trace()
                        
                        return StepResult(
                            action="response",
                            content=error_msg
                        )
                
                elif result.action == "module_call":
                    # Handle external module call  
                    target_action = result.module_name
                    module_input = result.module_input.get('input', result.module_input)
                    
                    # Find the target module by name
                    target_module_name = None
                    if target_action in client()._modules:
                        target_module_name = target_action
                    
                    # Find and execute the target module
                    if target_module_name:
                        # Record the module call
                        module_call_data = {
                            'action': target_action,
                            'module': target_module_name,
                            'input': module_input
                        }
                        self.module_calls.append(module_call_data)
                        
                        # Log module call
                        self.log_trace_event("module_call", {
                            "action": target_action,
                            "target_module": target_module_name,
                            "input": str(module_input)
                        })
                        
                        target_module = client()._modules[target_module_name]
                        target_instance = ModuleInstance(target_module, {})
                        module_result = target_instance.call(module_input)
                        
                        # Add the result to our module call record
                        self.module_calls[-1]['output'] = str(module_result)
                        
                        # Log module result
                        self.log_trace_event("module_call", {
                            "action": f"{target_action}_result",
                            "output": str(module_result)
                        })
                        
                        # Check if we need to continue ReAct flow
                        if 'context' in result.module_input:
                            # This was a ReAct step call - feed result back to react_step
                            context = result.module_input['context']
                            
                            # Continue with react_step using the module result as observation
                            result = StepResult(
                                action="step_call",
                                content="Continuing ReAct with observation",
                                module_name="react_step",
                                module_input={"context": context, "previous_action_result": str(module_result)}
                            )
                            # Don't save trace yet - continue processing
                        else:
                            # Regular module call - return the result
                            self.save_trace()
                            return StepResult(
                                action="response",
                                content=str(module_result)
                            )
                    else:
                        error_msg = f"No module found to handle action '{target_action}'"
                        self.log_trace_event("step", {
                            "step_name": "error",
                            "error": error_msg
                        })
                        self.save_trace()
                        
                        return StepResult(
                            action="response",
                            content=error_msg
                        )
            
            # Save trace for direct responses
            self.save_trace()
            return result
        else:
            error_msg = f"No start step defined for module {self.module.name}"
            self.log_trace_event("step", {
                "step_name": "error",
                "error": error_msg
            })
            self.save_trace()
            raise ValueError(error_msg)