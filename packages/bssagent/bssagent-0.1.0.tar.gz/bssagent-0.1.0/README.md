# BSS Agent

A comprehensive AI agent framework built with LangChain and LangGraph for business support systems.

## Features
- **Authentication**: Support client access via API Key.
- **Server API**: 
    - FastAPI-based REST API
    - Support agent response streaming
- **Security**: 
    - Rate limiter to avoid DDOS
    - Data Privacy protector
    - Prompt santinizer.
- **Environment Management**: Configuration and environment handling
- **Database Integration**:
    - For checkpoints
    - For long memory context (store)
    - Multi DB connection
- **RAGPipeline**:
    - Extract data from multi sources
    - Automatic create embedding model based on name
    - Easy to use Vector DB
- **Core Framework**: Base agent and multi user sessions management
- **Testing**: Comprehensive unit test for all features

## Installation

### From PyPI

```bash
pip install bssagent
```

### From Source

```bash
git clone https://github.com/bssagent/bssagent.git
cd bssagent
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/bssagent/bssagent.git
cd bssagent
pip install -e ".[dev]"
```

## Quick Start

```python
from bssagent.core import BSSAgent
from bssagent.environment import EnvironmentManager

# Initialize environment
env_manager = EnvironmentManager()
env_manager.load_config()

# Create agent
agent = BSSAgent(
    name="business_agent",
    description="Business support agent",
    tools=["file_io", "api_integration", "database"]
)

# Run agent
response = agent.run("Analyze the current business metrics")
print(response)
```

## Project Structure

```
bssagent/
├── src/bssagent/
│   ├── core/           # Core agent framework
│   ├── infrastructure/ # Infrastructure management
│   ├── deployment/     # Deployment tools
│   ├── serverapi/      # API server
│   ├── security/       # Security features
│   ├── environment/    # Environment management
│   ├── mcp/           # Model Context Protocol
│   ├── tools/         # Tool ecosystem
│   ├── database/      # Database integration
│   └── shared/        # Shared utilities
├── tests/             # Test suite
├── docs/              # Documentation
├── examples/          # Usage examples
└── scripts/           # Utility scripts
```

## Configuration

Create a `.env` file in your project root:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/bssagent

# API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Security
SECRET_KEY=your_secret_key
JWT_SECRET=your_jwt_secret

# Infrastructure
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AZURE_SUBSCRIPTION_ID=your_azure_subscription
GCP_PROJECT_ID=your_gcp_project
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=bssagent

# Run specific test categories
pytest -m unit
pytest -m integration
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

### Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

## Documentation

- [API Reference](https://bssagent.readthedocs.io/en/latest/api/)
- [User Guide](https://bssagent.readthedocs.io/en/latest/user_guide/)
- [Developer Guide](https://bssagent.readthedocs.io/en/latest/developer/)
- [Deployment Guide](https://bssagent.readthedocs.io/en/latest/deployment/)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- Documentation: https://bssagent.readthedocs.io
- Issues: https://github.com/bssagent/bssagent/issues
- Discussions: https://github.com/bssagent/bssagent/discussions
- Email: team@bssagent.com

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history. 