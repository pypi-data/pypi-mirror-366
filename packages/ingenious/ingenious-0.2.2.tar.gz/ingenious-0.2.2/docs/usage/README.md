---
title: "Usage Examples"
layout: single
permalink: /usage/
sidebar:
  nav: "docs"
toc: true
toc_label: "Usage Examples"
toc_icon: "play"
---

This guide shows how to use Insight Ingenious for various tasks.

## Getting Started

### Prerequisites

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) for Python package management

### Installation

```bash
# Install from your existing ingenious directory
uv add ingenious

# Initialize project (creates config templates and folder structure)
uv run ingen init
```

### Basic Configuration

1. Create a `.env` file in your project directory
2. Add your configuration using environment variables with `INGENIOUS_` prefix
3. Example `.env` file:
    ```bash
    # Model configuration
    INGENIOUS_MODELS__0__MODEL=gpt-4o-mini
    INGENIOUS_MODELS__0__API_KEY=your-api-key
    INGENIOUS_MODELS__0__BASE_URL=https://your-resource.openai.azure.com/

    # Chat service
    INGENIOUS_CHAT_SERVICE__TYPE=multi_agent
    ```

### Quick Setup Check

```bash
# Check your configuration status
uv run ingen status

# Get comprehensive help
uv run ingen help
```

## Understanding Workflows

Insight Ingenious provides multiple conversation workflows, each with different capabilities and configuration requirements:

### Check Workflow Requirements

Before using any workflow, check what configuration is needed:

```bash
# See all available workflows
uv run ingen workflows

# Check specific workflow requirements
uv run ingen workflows classification-agent
uv run ingen workflows knowledge-base-agent
```

### Quick Start Workflows (Minimal Configuration)

These workflows only need Azure OpenAI configuration:

- **classification-agent**: Routes input to specialized agents
- **bike-insights**: Sample domain-specific analysis

```bash
# Test minimal configuration workflow
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"user_prompt": "Hello", "conversation_flow": "classification-agent"}'
```

### Advanced Workflows (External Services Required)

- **knowledge-base-agent**: Requires Azure Cognitive Search or uses local ChromaDB (stable)
- **sql-manipulation-agent**: Requires database connection or uses local SQLite (stable)

For detailed setup instructions, see [Workflow Configuration Requirements](../workflows/README.md).

## Using the CLI

Insight Ingenious provides an intuitive command-line interface:

### Core Commands

```bash
# Initialize a new project
uv run ingen init

# Check configuration status
uv run ingen status

# Start the API server
uv run ingen serve

# List available workflows
uv run ingen workflows

# Run tests
uv run ingen test

# Get comprehensive help
uv run ingen help
```

### Server Management

```bash
# Start server with default settings
uv run ingen serve

# Start with custom port
uv run ingen serve --port 8080

# Start without prompt tuner
uv run ingen serve --no-prompt-tuner
```

### Testing and Development

```bash
# Run all tests
uv run ingen test

# Run tests with debug logging
uv run ingen test --log-level DEBUG

# Start prompt tuner standalone
uv run ingen prompt-tuner --port 5000
```
- `--run-args`: Key-value pairs for test runner (e.g., `--run-args='--test_name=TestName --test_type=TestType'`)

### Prompt Tuner (Integrated with FastAPI)

The prompt tuner is integrated with the main FastAPI application and accessible at `/prompt-tuner/`. It is enabled by default.

To run the application with the prompt tuner:

```bash
uv run ingen serve  # Prompt tuner is enabled by default
```

To disable the prompt tuner:

```bash
uv run ingen serve --no-prompt-tuner
```

The prompt tuner will be accessible at `http://localhost:{port}/prompt-tuner/` where `{port}` is the port you specified (default is 80).

### Data Preparation

```bash
uv run ingen dataprep [COMMAND]
```

Data-preparation utilities including the Scrapfly crawler façade. Use `uv run ingen dataprep --help` for more details.

## Using the Web UI

### Accessing the UI

Once the application is running, access the API at:
- http://localhost:8000 - Main API server (when using `--port 8000`)
- http://localhost:8000/docs - Interactive API documentation (Swagger UI)

Note: The default port is 80, but for local development it's recommended to use port 8000 with `ingen serve --port 8000`.

### Chatting with Agents via API

1. Use the REST API endpoint at `http://localhost:8000/api/v1/chat`
2. Send a POST request with your message and conversation flow
3. Example using curl:
   ```bash
   curl -X POST http://localhost:8000/api/v1/chat \
     -H "Content-Type: application/json" \
     -d '{
       "user_prompt": "Hello",
       "conversation_flow": "classification-agent"
     }'
   ```
4. The appropriate agents will process your request and respond

### Tuning Prompts

1. Navigate to http://localhost:{port}/prompt-tuner/ (where {port} is your configured port, default 80)
2. The prompt tuner interface is enabled by default (disable with `--no-prompt-tuner` flag)
3. Select the prompt template you want to edit
4. Make changes and test with sample data
5. Save revisions for version control

## Creating Custom Agents

### Custom Agent Structure

1. Create a new agent folder in `ingenious/services/chat_services/multi_agent/agents/your_agent_name/`
2. Create these files:
   - `agent.md`: Agent definition and persona
   - `tasks/task.md`: Task description for the agent

### Agent Definition Example

```markdown
# Your Agent Name

## Name and Persona

* Name: Your name is Ingenious and you are a [Specialty] Expert
* Description: You are a [specialty] expert assistant. Your role is to [description of responsibilities].

## System Message

### Backstory

[Background information about the agent's role and knowledge]

### Instructions

[Detailed instructions on how the agent should operate]

### Examples

[Example interactions or outputs]
```

## Creating Custom Conversation Patterns

### Pattern Structure

1. Create a new pattern module in `ingenious/services/chat_services/multi_agent/conversation_patterns/your_pattern_name/`
2. Implement the `ConversationPattern` class following the interface
3. Create a corresponding flow in `ingenious/services/chat_services/multi_agent/conversation_flows/your_pattern_name/`

### Pattern Implementation Example

```python
# conversation_patterns/your_pattern_name/your_pattern_name.py
import autogen
import logging

class ConversationPattern:
    def __init__(self, default_llm_config: dict, topics: list, memory_record_switch: bool, memory_path: str, thread_memory: str):
        self.default_llm_config = default_llm_config
        self.topics = topics
        self.memory_record_switch = memory_record_switch
        self.memory_path = memory_path
        self.thread_memory = thread_memory

        # Initialize agents
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            system_message="I represent the user's request"
        )

        self.your_agent = autogen.AssistantAgent(
            name="your_agent",
            system_message="Your agent's system message",
            llm_config=self.default_llm_config
        )

    async def get_conversation_response(self, input_message: str) -> [str, str]:
        # Set up agent interactions
        result = await self.user_proxy.a_initiate_chat(
            self.your_agent,
            message=input_message
        )

        return result.summary, ""
```

### Flow Implementation Example

```python
# conversation_flows/your_pattern_name/your_pattern_name.py
from ingenious.models.chat import ChatResponse
from ingenious.services.chat_services.multi_agent.conversation_patterns.your_pattern_name.your_pattern_name import ConversationPattern

class ConversationFlow:
    @staticmethod
    async def get_conversation_response(message: str, topics: list = [], thread_memory: str='', memory_record_switch = True, thread_chat_history: list = []) -> ChatResponse:
        # Get configuration
        import ingenious.config.config as config
        _config = config.get_config()
        llm_config = _config.models[0].__dict__
        memory_path = _config.chat_history.memory_path

        # Initialize the conversation pattern
        agent_pattern = ConversationPattern(
            default_llm_config=llm_config,
            topics=topics,
            memory_record_switch=memory_record_switch,
            memory_path=memory_path,
            thread_memory=thread_memory
        )

        # Get the conversation response
        res, memory_summary = await agent_pattern.get_conversation_response(message)

        return res, memory_summary
```

## Using Custom Templates

### Creating Custom Prompts

1. Create a new template in `templates/prompts/your_prompt_name.jinja`
2. Use Jinja2 syntax for dynamic content

Example:
```jinja
I am an agent tasked with providing insights about {{ topic }} based on the input payload.

User input: {{ user_input }}

Please provide a detailed analysis focusing on:
1. Key facts
2. Relevant context
3. Potential implications

Response format:
{
  "analysis": {
    "key_facts": [],
    "context": "",
    "implications": []
  },
  "recommendation": ""
}
```

### Using Templates in Agents

```python
async def get_conversation_response(self, chat_request: ChatRequest) -> ChatResponse:
    # Load the template
    template_content = await self.Get_Template(file_name="your_prompt_name.jinja")

    # Render the template with dynamic values
    env = Environment()
    template = env.from_string(template_content)
    rendered_prompt = template.render(
        topic="example topic",
        user_input=chat_request.user_prompt
    )

    # Use the rendered prompt
    your_agent.system_prompt = rendered_prompt
```

## API Integration

### Understanding Workflow Requirements

Before using the REST API, understand which workflows need external service configuration:

```bash
# Check all workflow requirements
uv run ingen workflows

# Check specific workflow
uv run ingen workflows knowledge-base-agent
```

### Using the REST API

You can interact with Insight Ingenious through its REST API:

#### Minimal Configuration Workflows
These work with just Azure OpenAI setup:

```bash
# Classification agent - route input to specialized agents
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n username:password | base64)" \
  -d '{
    "user_prompt": "Analyze this customer feedback: Great product!",
    "conversation_flow": "classification-agent"
  }'

# Bike insights - sample domain-specific workflow
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Show bike sales trends",
    "conversation_flow": "bike-insights"
  }'
```

#### Local Knowledge Base (Default Implementation)
Uses local ChromaDB for vector search when Azure Search is not configured:

```bash
# Knowledge base search using local ChromaDB
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Search for health and safety information",
    "conversation_flow": "knowledge-base-agent"
  }'
```

**Configuration needed**: None! Just add documents to `./.tmp/knowledge_base/`

#### Local Database (Default Implementation)
Uses local SQLite database when Azure SQL is not configured:

```bash
# SQL queries using local SQLite
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Show me student performance statistics",
    "conversation_flow": "sql-manipulation-agent"
  }'
```

**Configuration needed**: Set `INGENIOUS_AZURE_SQL_SERVICES__DATABASE_NAME=skip` in environment to enable SQLite mode

#### Azure Service Integrations

When configured with Azure services, the workflows can use:

**Azure Cognitive Search** for knowledge-base-agent:
- Configure with environment variables: `INGENIOUS_AZURE_SEARCH_SERVICES__ENDPOINT` and `INGENIOUS_AZURE_SEARCH_SERVICES__KEY`
- Provides enterprise-scale search capabilities

**Azure SQL Database** for sql-manipulation-agent:
- Configure with full Azure SQL connection details
- Supports production database workloads

### Error Responses

When workflows can't run due to missing configuration:

```json
{
  "error": "Azure Search service not configured",
  "workflow": "knowledge-base-agent",
  "required_config": ["azure_search_services.endpoint", "azure_search_services.key"],
  "documentation": "See docs/workflows/README.md for setup instructions"
}
```

### Checking Configuration Status

```bash
# Check if configuration is complete for a workflow
curl -X GET http://localhost:80/api/v1/workflow-status/knowledge-base-agent
```

Response:
```json
{
  "workflow": "knowledge-base-agent",
  "configured": true,
  "missing_config": [],
  "ready": true
}
```

### Creating Custom API Routes

1. Create a new route module in `ingenious_extensions_template/api/routes/custom.py`
2. Implement the `Api_Routes` class

Example:
```python
from fastapi import APIRouter, Depends, FastAPI
from ingenious.models.api_routes import IApiRoutes
from ingenious.models.config import Config

class Api_Routes(IApiRoutes):
    def __init__(self, config: Config, app: FastAPI):
        self.config = config
        self.app = app
        self.router = APIRouter()

    def add_custom_routes(self):
        @self.router.get("/api/v1/custom-endpoint")
        async def custom_endpoint():
            return {"message": "Custom endpoint response"}

        self.app.include_router(self.router)
```
