
# AI Mesh SDK

A lightweight Python SDK for discovering and calling agents on the AI Mesh platform.

## Features
- List available agents on the mesh
- Call any agent by ID with custom inputs
- Convert all Mesh agents into LangChain-compatible tools
- Simple authentication with API tokens

## Installation

```bash
pip install ai-mesh-sdk
```

## Quick Start

```python
from mesh_sdk import MeshSDK

# Initialize with your API token
sdk = MeshSDK(token="your-api-token")

# List all available agents
agents = sdk.list_agents()
print(f"Found {len(agents)} agents")

# Call a specific agent
result = sdk.call_agent(
    agent_id="agent-123",
    inputs={"prompt": "Hello, world!"}
)
print(result)

# Use with LangChain
from langchain.agents import initialize_agent, AgentType

tools = sdk.to_langchain_tools()
agent = initialize_agent(
    tools=tools,
    llm=your_llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)
```

## API Reference

### MeshSDK(token)
Initialize the SDK with your API token.

**Parameters:**
- `token` (str): Your AI Mesh API token

### list_agents()
Returns a list of all available agents on the mesh.

**Returns:** List[Dict] - Agent metadata including ID, name, and description

### call_agent(agent_id, inputs)
Call a specific agent with provided inputs.

**Parameters:**
- `agent_id` (str): The unique identifier of the agent
- `inputs` (Dict): Input parameters for the agent

**Returns:** Dict - The agent's response

### to_langchain_tools()
Convert all mesh agents into LangChain Tool objects.

**Returns:** List[Tool] - LangChain-compatible tools

## License

MIT License