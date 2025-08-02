# Contributing to GoFastAPI

Thank you for considering contributing to GoFastAPI! This document provides guidelines and information for contributors.

## 🌟 Ways to Contribute

### 🐛 Bug Reports
- Use the GitHub issue tracker
- Include detailed reproduction steps
- Provide system information
- Include relevant logs and error messages

### ✨ Feature Requests
- Check existing issues first
- Use GitHub Discussions for ideas
- Provide clear use cases
- Consider implementation complexity

### 🔧 Code Contributions
- Bug fixes
- New features
- Performance improvements
- Documentation updates
- Test coverage improvements

### 📚 Documentation
- API documentation
- Tutorials and guides
- Example projects
- Blog posts and articles

## 🚀 Getting Started

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/gofastapi.git
   cd gofastapi/pythonpackaging
   ```

2. **Setup Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   
   # Install development dependencies
   pip install -e .[dev]
   
   # Setup development tools
   python scripts/dev.py setup
   ```

3. **Verify Setup**
   ```bash
   # Run tests
   python scripts/test.py all
   
   # Check code quality
   python scripts/dev.py lint
   ```

## 🔄 Development Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 2. Make Changes
- Write clean, readable code
- Follow existing code style
- Add tests for new functionality
- Update documentation if needed

### 3. Test Your Changes
```bash
# Run specific tests
python scripts/test.py unit
python scripts/test.py integration

# Run all tests with coverage
python scripts/test.py all

# Performance tests (for performance changes)
python scripts/test.py performance
```

### 4. Check Code Quality
```bash
# Auto-fix formatting
python scripts/dev.py fix

# Run linters
python scripts/dev.py lint

# Type checking
mypy gofastapi/
```

### 5. Commit Changes
```bash
git add .
git commit -m "feat: add amazing new feature"

# Follow conventional commits format:
# feat: new feature
# fix: bug fix
# docs: documentation update
# test: add tests
# refactor: code refactoring
# perf: performance improvement
```

### 6. Submit Pull Request
- Push branch to your fork
- Create PR against main branch
- Fill out PR template
- Wait for review

## 📋 Code Style Guidelines

### Python Code Style
- **Formatter**: Black (line length 88)
- **Import sorting**: isort
- **Linting**: flake8, mypy
- **Docstrings**: Google style

```python
def example_function(param1: str, param2: int = 10) -> dict:
    """Example function with proper typing and docstring.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2
        
    Returns:
        Dictionary with result data
        
    Raises:
        ValueError: If param1 is empty
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    
    return {"param1": param1, "param2": param2}
```

### Go Code Style (for Go components)
- **Formatter**: gofmt
- **Linting**: golangci-lint
- **Documentation**: Go doc comments

### Commit Message Format
Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

body (optional)

footer (optional)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Maintenance

Examples:
```
feat(api): add user authentication endpoint
fix(runtime): resolve memory leak in subinterpreter pool
docs(readme): update installation instructions
test(cli): add integration tests for dev command
```

## 🧪 Testing Guidelines

### Test Structure
```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── performance/    # Performance benchmarks
├── fixtures/       # Test data and fixtures
└── conftest.py     # pytest configuration
```

### Writing Tests
```python
import pytest
from gofastapi import GoFastAPI
from gofastapi.testing import TestClient

class TestUserAPI:
    @pytest.fixture
    def app(self):
        app = GoFastAPI()
        
        @app.get("/users/{user_id}")
        def get_user(user_id: int):
            return {"user_id": user_id}
            
        return app
    
    @pytest.fixture
    def client(self, app):
        return TestClient(app)
    
    def test_get_user_success(self, client):
        response = client.get("/users/123")
        assert response.status_code == 200
        assert response.json()["user_id"] == 123
    
    def test_get_user_invalid_id(self, client):
        response = client.get("/users/abc")
        assert response.status_code == 422
```

### Performance Tests
```python
import pytest
from gofastapi.testing import PerformanceTest

def test_endpoint_performance():
    test = PerformanceTest(app)
    result = test.benchmark_endpoint(
        "/users/123",
        duration=10,  # seconds
        concurrency=100
    )
    
    # Assert performance requirements
    assert result.requests_per_second > 10000
    assert result.average_latency < 5  # milliseconds
    assert result.p95_latency < 10
```

## 📖 Documentation Guidelines

### API Documentation
- Use clear, descriptive docstrings
- Include parameter types and descriptions
- Provide examples
- Document exceptions

### README Updates
- Keep examples current
- Update performance benchmarks
- Add new features to feature list
- Update installation instructions

### Changelog
- Follow Keep a Changelog format
- Include breaking changes
- Note performance impacts
- Provide migration guidance

## 🚢 Release Process

### Version Numbers
Follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist
1. Update version in `gofastapi/version.py`
2. Update CHANGELOG.md
3. Run full test suite
4. Build and test package
5. Create GitHub release
6. Publish to PyPI

## 🏆 Recognition

### Contributors
All contributors are recognized in:
- GitHub contributors list
- CHANGELOG.md acknowledgments
- Annual contributor highlights

### Contribution Types
We recognize all types of contributions:
- 💻 Code
- 📖 Documentation
- 🐛 Bug reports
- 💡 Ideas and suggestions
- 🎨 Design
- ⚡ Performance improvements
- 🧪 Testing
- 🌍 Translation

## 📞 Getting Help

### Development Questions
- **GitHub Discussions**: For general questions
- **Discord**: Real-time chat with maintainers
- **Stack Overflow**: Tag with `gofastapi`

### Code Review Process
1. **Automated Checks**: CI/CD runs tests and linting
2. **Maintainer Review**: Core team reviews code
3. **Community Review**: Community feedback welcome
4. **Final Approval**: Maintainer approval required

### Review Criteria
- **Functionality**: Does it work as expected?
- **Tests**: Adequate test coverage?
- **Documentation**: Is it documented?
- **Performance**: No performance regressions?
- **Style**: Follows code style guidelines?
- **Breaking Changes**: Are they necessary and documented?

## 🎯 Contribution Areas

### High Priority
- 🐛 Bug fixes
- 📚 Documentation improvements
- 🧪 Test coverage increases
- ⚡ Performance optimizations

### Feature Development
- 🔌 Plugin system
- 🌐 WebSocket support
- 📊 Enhanced monitoring
- 🔐 Security features

### Community
- 📝 Tutorial creation
- 🎥 Video content
- 🗣️ Conference talks
- 📰 Blog posts

## 📜 Code of Conduct

### Our Pledge
We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards
**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Harassment in any form
- Discriminatory language or actions
- Personal attacks or insults
- Publishing private information without permission
- Other conduct inappropriate in a professional setting

### Enforcement
Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project team at conduct@gofastapi.dev. All complaints will be reviewed and investigated promptly and fairly.

## 🙏 Thank You

Thank you for contributing to GoFastAPI! Your contributions help make this project better for everyone in the Python community.

---

**Questions?** Feel free to reach out:
- 📧 Email: contributors@gofastapi.dev
- 💬 Discord: [GoFastAPI Community](https://discord.gg/gofastapi)
- 🐙 GitHub: [Discussions](https://github.com/coffeecms/gofastapi/discussions)
