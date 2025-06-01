# Contributing to InfluencerFlow AI Platform

Thank you for your interest in contributing to InfluencerFlow! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Types of Contributions

We welcome several types of contributions:

- **🐛 Bug Reports**: Help us identify and fix issues
- **✨ Feature Requests**: Suggest new functionality
- **📖 Documentation**: Improve our documentation
- **🔧 Code Contributions**: Add features or fix bugs
- **🧪 Testing**: Help improve test coverage
- **🎨 UI/UX Improvements**: Enhance user experience

## 🚀 Getting Started

### Development Setup

1. **Fork the Repository**
```bash
git clone https://github.com/your-username/influencer-ai-backend.git
cd influencer-ai-backend
```

2. **Set Up Development Environment**
```bash
# Run the setup script
python setup.py

# Or manually:
uv sync  # or pip install -r requirements.txt
cp .env.template .env
# Edit .env with your API keys
```

3. **Install Development Tools**
```bash
uv add --dev pytest black flake8 mypy pre-commit
# or
pip install pytest black flake8 mypy pre-commit
```

4. **Set Up Pre-commit Hooks**
```bash
pre-commit install
```

5. **Verify Setup**
```bash
python test_setup.py
uvicorn main:app --reload
```

### Project Structure Understanding

```
influencer-ai-backend/
├── agents/           # AI agents (orchestrator, discovery, negotiation, contracts)
├── api/             # FastAPI route handlers
├── services/        # External service integrations
├── models/          # Data models and schemas
├── config/          # Configuration management
├── data/           # Static data files
└── tests/          # Test files
```

## 📝 Development Guidelines

### Code Style

We follow PEP 8 with some customizations:

```bash
# Format code
black .

# Check style
flake8 .

# Type checking
mypy .
```

#### Key Style Guidelines

- **Line Length**: 88 characters (Black default)
- **Imports**: Use absolute imports, group by standard/third-party/local
- **Docstrings**: Use Google-style docstrings
- **Type Hints**: Use type hints for all public functions
- **Logging**: Use structured logging with appropriate levels

### Code Examples

#### Function Documentation
```python
async def negotiate_with_creator(
    creator: Creator, 
    campaign: CampaignData,
    strategy: Optional[Dict[str, Any]] = None
) -> NegotiationResult:
    """
    Conduct AI-powered negotiation with creator.
    
    Args:
        creator: Creator profile with contact information
        campaign: Campaign details and requirements  
        strategy: Optional AI strategy configuration
        
    Returns:
        NegotiationResult containing outcome and terms
        
    Raises:
        NegotiationError: If negotiation fails due to system error
        ValidationError: If input data is invalid
    """
    # Implementation here
```

#### Error Handling
```python
import logging

logger = logging.getLogger(__name__)

try:
    result = await some_operation()
    logger.info(f"✅ Operation successful: {result.id}")
    return result
except SpecificError as e:
    logger.error(f"❌ Specific error occurred: {e}")
    raise
except Exception as e:
    logger.error(f"❌ Unexpected error: {e}")
    raise SystemError(f"Operation failed: {str(e)}")
```

#### Class Structure
```python
class MyAgent:
    """
    Agent for handling specific functionality.
    
    Attributes:
        service: External service integration
        config: Agent configuration
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize agent with configuration."""
        self.service = SomeService()
        self.config = config or {}
        logger.info("🤖 MyAgent initialized")
    
    async def process(self, data: InputData) -> OutputData:
        """Process data according to agent logic."""
        # Implementation
```

### Testing Guidelines

#### Test Structure
```python
import pytest
from unittest.mock import Mock, patch
from agents.my_agent import MyAgent

class TestMyAgent:
    """Test suite for MyAgent functionality."""
    
    @pytest.fixture
    def mock_agent(self):
        """Create mock agent for testing."""
        return MyAgent(config={"test_mode": True})
    
    @pytest.mark.asyncio
    async def test_successful_processing(self, mock_agent):
        """Test successful data processing."""
        # Arrange
        input_data = InputData(value="test")
        
        # Act
        result = await mock_agent.process(input_data)
        
        # Assert
        assert result.success is True
        assert result.value == "processed_test"
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_agent):
        """Test error handling in processing."""
        # Test error scenarios
```

#### Test Categories

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test service integrations
- **End-to-End Tests**: Test complete workflows
- **Mock Tests**: Test with external service mocks

#### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agents.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run only unit tests
pytest -m unit

# Run only integration tests  
pytest -m integration
```

## 🔄 Development Workflow

### Branch Naming

- **Feature**: `feature/creator-discovery-enhancement`
- **Bug Fix**: `bugfix/negotiation-timeout-issue`
- **Documentation**: `docs/api-documentation-update`
- **Refactor**: `refactor/voice-service-cleanup`

### Commit Messages

Follow conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Examples:
```
feat(agents): add AI-powered negotiation strategy generation

- Implement Groq-based strategy analysis
- Add creator-specific approach customization
- Include market data integration

Closes #123
```

```
fix(voice): resolve ElevenLabs connection timeout issue

- Increase connection timeout to 30 seconds
- Add retry logic for failed connections
- Improve error messaging

Fixes #456
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Pull Request Process

1. **Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
git push -u origin feature/your-feature-name
```

2. **Make Changes**
   - Write code following style guidelines
   - Add/update tests
   - Update documentation if needed

3. **Test Changes**
```bash
# Run tests
pytest

# Check code style
black . && flake8 .

# Test installation
python test_setup.py
```

4. **Commit Changes**
```bash
git add .
git commit -m "feat(scope): description"
git push
```

5. **Create Pull Request**
   - Use PR template
   - Include description of changes
   - Reference related issues
   - Add screenshots if UI changes

### PR Template

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes (or breaking changes documented)

## Related Issues
Closes #issue_number
```

## 🧪 Testing Contributions

### Test Requirements

All contributions should include appropriate tests:

- **New Features**: Unit tests + integration tests
- **Bug Fixes**: Regression tests
- **Refactoring**: Ensure existing tests still pass

### Test Data

Use consistent test data:

```python
# Test fixtures
@pytest.fixture
def sample_creator():
    """Sample creator for testing."""
    return Creator(
        id="test_creator",
        name="Test Creator",
        platform="Instagram",
        followers=100000,
        niche="fitness",
        typical_rate=3000,
        engagement_rate=5.5,
        # ... other fields
    )

@pytest.fixture  
def sample_campaign():
    """Sample campaign for testing."""
    return CampaignData(
        id="test_campaign",
        product_name="Test Product",
        brand_name="Test Brand",
        total_budget=10000,
        # ... other fields
    )
```

## 📖 Documentation Contributions

### Documentation Types

- **API Documentation**: Docstrings and OpenAPI specs
- **User Documentation**: README, setup guides
- **Developer Documentation**: Architecture, contributing guides
- **Code Comments**: Inline explanations

### Documentation Standards

- **Clear and Concise**: Easy to understand
- **Up-to-Date**: Reflect current functionality
- **Examples**: Include code examples
- **Searchable**: Use proper headings and structure

## 🐛 Bug Reports

### Bug Report Template

```markdown
**Bug Description**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. Call endpoint '....'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g. Ubuntu 22.04]
- Python Version: [e.g. 3.13.1]
- Package Version: [e.g. 1.0.0]

**Additional Context**
- Error logs
- Screenshots
- Configuration details
```

## ✨ Feature Requests

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features you've considered.

**Additional context**
- Use cases
- Examples from other systems
- Implementation suggestions
```

## 🔧 Architecture Guidelines

### Adding New Agents

1. **Create Agent Class**
```python
# agents/my_new_agent.py
class MyNewAgent:
    """Agent for specific functionality."""
    
    def __init__(self):
        self.initialized = True
    
    async def process(self, data):
        """Main processing method."""
        pass
```

2. **Update Orchestrator**
```python
# In orchestrator.py
async def _run_my_new_phase(self, state):
    """Add new processing phase."""
    agent = MyNewAgent()
    result = await agent.process(state.data)
    state.my_new_result = result
```

3. **Add Tests**
```python
# tests/test_my_new_agent.py
class TestMyNewAgent:
    """Test suite for new agent."""
    pass
```

### Adding New Services

1. **Create Service Class**
```python
# services/my_service.py
class MyService:
    """Integration with external service."""
    
    def __init__(self):
        self.api_key = settings.my_service_api_key
    
    async def call_api(self, data):
        """Make API call."""
        pass
```

2. **Add Configuration**
```python
# In config/settings.py
my_service_api_key: Optional[str] = None
```

3. **Update Environment Template**
```bash
# In .env.template
MY_SERVICE_API_KEY=your_api_key_here
```

## 📊 Performance Guidelines

### Async Best Practices

```python
# Good: Use async/await properly
async def process_multiple(items):
    tasks = [process_item(item) for item in items]
    results = await asyncio.gather(*tasks)
    return results

# Bad: Blocking in async function
async def bad_process(items):
    results = []
    for item in items:
        result = await process_item(item)  # Sequential processing
        results.append(result)
    return results
```

### Database Best Practices

```python
# Good: Use connection pooling
async with db_pool.acquire() as connection:
    result = await connection.execute(query)

# Good: Batch operations
await connection.executemany(query, data_batch)
```

### Error Handling Best Practices

```python
# Good: Specific error handling
try:
    result = await external_api_call()
except APITimeoutError:
    logger.warning("API timeout, using cached data")
    result = get_cached_data()
except APIError as e:
    logger.error(f"API error: {e}")
    raise
```

## 🚦 Release Process

### Version Numbering

We use semantic versioning (SemVer):
- **Major** (1.0.0): Breaking changes
- **Minor** (1.1.0): New features, backward compatible
- **Patch** (1.1.1): Bug fixes, backward compatible

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version number updated
- [ ] Changelog updated
- [ ] Security review completed
- [ ] Performance testing completed

## 📞 Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Code Review**: PR comments and feedback

### Questions?

If you have questions about contributing:

1. Check existing issues and discussions
2. Review this contributing guide
3. Create a new discussion or issue
4. Reach out to maintainers

## 🏆 Recognition

Contributors will be recognized in:
- **README.md**: Contributors section
- **Release Notes**: Major contribution mentions
- **GitHub**: Contributor statistics

Thank you for contributing to InfluencerFlow AI Platform! 🎉