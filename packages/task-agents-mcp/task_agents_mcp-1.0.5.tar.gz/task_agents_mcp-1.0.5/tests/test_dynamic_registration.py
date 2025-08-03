#!/usr/bin/env python3
"""
Test script to explore FastMCP dynamic registration capabilities
Phase 1: Infrastructure Setup - Research
"""
import asyncio
from fastmcp import FastMCP

# Test 1: Can we register prompts after FastMCP initialization?
print("=== Test 1: Post-initialization registration ===")

mcp = FastMCP("test-dynamic")

# Try registering a prompt using decorator after initialization
@mcp.prompt
def static_prompt():
    """A statically defined prompt"""
    return "This is a static prompt"

# The decorator returns a different object, not the function itself
print(f"Static prompt type: {type(static_prompt)}")
print(f"Static prompt attributes: {[attr for attr in dir(static_prompt) if not attr.startswith('_')]}")

# Test 2: Can we use mcp.prompt as a function (not decorator)?
print("\n=== Test 2: Functional registration ===")

def dynamic_prompt_1():
    """A dynamically defined prompt"""
    return "This is dynamic prompt 1"

# Try to register it functionally
try:
    # This mimics what the decorator does
    dynamic_prompt_registered = mcp.prompt(dynamic_prompt_1)
    print(f"Dynamic prompt 1 registered functionally: {dynamic_prompt_1.__name__}")
except Exception as e:
    print(f"Failed to register functionally: {e}")

# Test 3: Factory pattern for creating prompts
print("\n=== Test 3: Factory pattern ===")

def create_agent_prompt(agent_name: str):
    """Factory to create a prompt function for a specific agent"""
    def agent_prompt(task: str = ""):
        return f"Please use the {agent_name} agent to: {task or 'perform its specialized task'}"
    
    # Set meaningful name and docstring
    agent_prompt.__name__ = f"{agent_name.lower().replace(' ', '_')}_task"
    agent_prompt.__doc__ = f"Generate a task for the {agent_name} agent"
    
    return agent_prompt

# Create prompts for multiple agents
test_agents = ["Code Reviewer", "Debugger", "Test Runner"]

for agent in test_agents:
    prompt_func = create_agent_prompt(agent)
    registered_func = mcp.prompt(prompt_func)
    print(f"Created prompt: {prompt_func.__name__}")

# Test 4: Check if we can inspect registered prompts
print("\n=== Test 4: Inspecting registered items ===")

# Try to access internal attributes (this is exploratory)
if hasattr(mcp, '_prompts'):
    print(f"Found _prompts attribute: {len(getattr(mcp, '_prompts', []))} prompts")
if hasattr(mcp, 'prompts'):
    print(f"Found prompts attribute: {len(getattr(mcp, 'prompts', []))} prompts")

# Look for any method to list registered items
for attr in dir(mcp):
    if 'prompt' in attr.lower() and not attr.startswith('_'):
        print(f"Found prompt-related attribute: {attr}")

# Test 5: Create a complete example with dynamic prompts
print("\n=== Test 5: Complete dynamic example ===")

class DynamicPromptServer:
    def __init__(self):
        self.mcp = FastMCP("dynamic-test")
        self.agents = {
            "Code Reviewer": "Review code for quality and security",
            "Debugger": "Debug and fix errors", 
            "Performance Optimizer": "Optimize code performance"
        }
        
    def register_dynamic_prompts(self):
        """Register prompts for all agents"""
        for agent_name, description in self.agents.items():
            prompt_func = self._create_prompt(agent_name, description)
            self.mcp.prompt(prompt_func)
            print(f"Registered prompt: {prompt_func.__name__}")
    
    def _create_prompt(self, agent_name: str, description: str):
        """Create a prompt function for an agent"""
        def prompt(task: str = "", include_description: bool = True):
            base = f"Use the {agent_name} agent to: {task or 'help with your task'}"
            if include_description:
                base += f"\n\nThis agent specializes in: {description}"
            return base
        
        # Clean name for function
        clean_name = agent_name.lower().replace(' ', '_')
        prompt.__name__ = f"{clean_name}_prompt"
        prompt.__doc__ = f"Create a task for {agent_name} - {description}"
        
        return prompt

# Test the dynamic server
server = DynamicPromptServer()
server.register_dynamic_prompts()

print("\n=== Summary ===")
print("1. FastMCP allows functional registration using mcp.prompt(func)")
print("2. We can create prompts dynamically using factory functions")
print("3. Registration must happen before mcp.run()")
print("4. Function names and docstrings can be set dynamically")