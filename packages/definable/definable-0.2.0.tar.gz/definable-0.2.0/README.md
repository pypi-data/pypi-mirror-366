# Definable

Infrastructure for building and deploying AI agents with a simple YAML configuration and base class extension pattern.

## Features

- **Simple Base Class**: Extend `AgentBox` to create your agent
- **YAML Configuration**: Configure builds with declarative YAML files
- **Docker Packaging**: Build Docker images with a single command
- **FastAPI Integration**: Automatic REST API generation with OpenAPI docs
- **CLI Tools**: Complete toolkit with init, build, serve, push, and config commands
- **Project Scaffolding**: Generate new agent projects with templates
- **Remote Deployment**: Push agents to deployment servers
- **Hook System**: Pre and post-processing hooks for middleware

## Quick Start

### 1. Install Definable

```bash
pip install definable
```

### 2. Initialize a New Project

```bash
# Create a new agent project with interactive prompts
definable init

# Or specify details directly
definable init --name my-agent --description "My custom agent" --version 1.0.0
```

This creates:
- `main.py` - Your agent implementation
- `agent.yaml` - Configuration file
- `.agentignore` - Files to exclude from builds
- `README.md` - Project documentation

### 3. Create Your Agent

The generated `main.py` provides a template, or create your own:

```python
# main.py
from definable import AgentBox, AgentInput, AgentOutput, AgentInfo
from pydantic import Field

class SampleAgentInput(AgentInput):
    message: str = Field(description="Input message to process")

class SampleAgentOutput(AgentOutput):
    response_message: str = Field(description="Processed response message")

class DemoAgent(AgentBox):
    def setup(self):
        """Initialize your agent - called once on startup"""
        self.name = 'demo-agent'
        self.version = '1.0.0'
        print("Demo agent initialized!")
    
    def invoke(self, agent_input: SampleAgentInput) -> SampleAgentOutput:
        """Main agent logic - called for each request"""
        processed_message = f"Processed: {agent_input.message.upper()}"
        return SampleAgentOutput(response_message=processed_message)
    
    def info(self) -> AgentInfo:
        """Return agent metadata for API documentation"""
        return AgentInfo(
            name=self.name,
            description="A simple demo agent that processes messages",
            version=self.version,
            input_schema=SampleAgentInput.model_json_schema(),
            output_schema=SampleAgentOutput.model_json_schema()
        )
```

### 4. Configure Your Agent

The `agent.yaml` file configures the build and deployment:

```yaml
# agent.yaml
build:
  python_version: "3.11"
  dependencies:
    - "requests>=2.28.0"
    - "openai"  # Add your specific dependencies
  system_packages:
    - "curl"
  environment_variables:
    - API_KEY  # Environment variables to pass through

agent: "main.py:DemoAgent"

platform:
  name: "demo-agent"
  description: "A simple demo agent for testing"
  version: "1.0.0"

concurrency:
  max_concurrent_requests: 50
  request_timeout: 300
```

### 5. Develop and Deploy

```bash
# Serve locally for development (includes hot reload)
definable serve -p 8000

# Build Docker image for production
definable build -t my-agent

# Push to deployment server (if configured)
definable push

# Manage configuration
definable config
```

## CLI Commands

- **`definable init`** - Initialize a new agent project with templates
- **`definable serve`** - Serve agent locally for development
- **`definable build`** - Build Docker image from agent configuration  
- **`definable push`** - Deploy agent to remote deployment server
- **`definable config`** - Manage global configuration settings

### CLI Options

```bash
# Serve with custom options
definable serve --port 3000 --host localhost --file custom-agent.yaml

# Build with custom tag and config
definable build -t my-agent:v1.2.0 -f production-agent.yaml

# Push with deployment options
definable push -n my-agent
```

## Advanced Features

### Hook System

Add pre and post-processing logic:

```python
class MyAgent(AgentBox):
    def pre_hook(self):
        """Called before invoke()"""
        print("Pre-processing...")
    
    def post_hook(self):
        """Called after invoke()"""
        print("Post-processing...")
```

### Flexible Input/Output

You can use any types for inputs and outputs:

```python
def invoke(self, agent_input: dict) -> str:
    """Simple string-to-string agent"""
    return f"Echo: {agent_input.get('message', '')}"
```

### Environment Configuration

The framework supports environment variables and secrets:

```yaml
build:
  environment_variables:
    - DATABASE_URL
    - API_SECRET
    - DEBUG=false
```

## API Documentation

When served, your agent automatically gets:
- **OpenAPI/Swagger docs** at `/docs`
- **Health check endpoint** at `/health`
- **Agent info endpoint** at `/info`

## Requirements

- **Python**: 3.9 or higher
- **Docker**: Required for building images
- **Dependencies**: FastAPI, Uvicorn, Pydantic, Click, Docker SDK


## License

MIT License - see LICENSE file for details.