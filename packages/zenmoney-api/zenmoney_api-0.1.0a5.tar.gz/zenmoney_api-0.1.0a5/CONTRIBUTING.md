# Contributing to ZenMoney API Client

Thank you for considering contributing to this project! Your help is greatly appreciated.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style and Standards](#code-style-and-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Pull Request Guidelines](#pull-request-guidelines)
- [GitHub Workflow Template](#github-workflow-template)

## Getting Started

### 1. Fork the Repository

Click the "Fork" button at the top right of this page to create your own copy of the repository.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/zenmoney-api.git
cd zenmoney-api
```

### 3. Add Upstream Remote

```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/zenmoney-api.git
```

## Development Setup

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

1. **Install uv** (if not already installed):
   ```bash
   pip install uv
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Activate the virtual environment**:
   ```bash
   uv shell
   ```

### Development Environment

The project uses several development tools:

- **uv**: Package and environment management
- **pytest**: Testing framework
- **mypy**: Static type checking
- **pylint**: Code linting
- **ruff**: Fast Python linter and formatter
- **pre-commit**: Git hooks for code quality

## Code Style and Standards

### Python Code Style

This project follows PEP 8 with some modifications:

- **Line length**: 88 characters (Black default)
- **Import sorting**: isort with Black profile
- **Type hints**: Required for all functions and methods
- **Docstrings**: Google style docstrings for public APIs

### Code Quality Tools

Run the following commands to ensure code quality:

```bash
# Format code with ruff
uv run ruff format .

# Lint code with ruff
uv run ruff check .

# Type checking with mypy
uv run mypy src/

# Lint with pylint
uv run pylint src/zenmoney_api/

# Run all quality checks
uv run pre-commit run --all-files
```

### Pre-commit Hooks

Install pre-commit hooks to automatically check code quality:

```bash
uv run pre-commit install
```

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/zenmoney_api --cov-report=html

# Run specific test file
uv run pytest tests/test_client.py

# Run tests with verbose output
uv run pytest -v
```

### Test Guidelines

- Write tests for all new functionality
- Use descriptive test names
- Follow the `test_*` naming convention
- Use pytest fixtures for common setup
- Aim for high test coverage (minimum 80%)

### Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── test_auth.py         # Authentication tests
├── test_client.py       # Client functionality tests
└── test_models.py       # Data model tests
```

## Submitting Changes

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write clear, descriptive commit messages
- Follow the existing code style
- Add tests for new functionality
- Update documentation if needed

### 3. Commit Your Changes

```bash
git add .
git commit -m "feat: add new feature description"
```

**Commit Message Format:**
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for code style changes
- `refactor:` for code refactoring
- `test:` for test additions/changes
- `chore:` for maintenance tasks

### 4. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 5. Create a Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Select your feature branch
4. Fill out the PR template
5. Submit the PR

## Pull Request Guidelines

### Before Submitting

- [ ] Code follows the project's style guidelines
- [ ] All tests pass
- [ ] New functionality has tests
- [ ] Documentation is updated if needed
- [ ] Type hints are added for new functions
- [ ] No linting errors (ruff, pylint, mypy)


## Additional Resources

- [Python Packaging User Guide](https://packaging.python.org/)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [pytest Documentation](https://docs.pytest.org/)
- [mypy Documentation](https://mypy.readthedocs.io/)

## Questions or Problems?

If you have questions or encounter problems:

1. Check the [Issues](https://github.com/ORIGINAL_OWNER/zenmoney-api/issues) page
2. Create a new issue with a clear description
3. Join our discussions in the [Discussions](https://github.com/ORIGINAL_OWNER/zenmoney-api/discussions) section

Thank you for contributing to ZenMoney API Client!
