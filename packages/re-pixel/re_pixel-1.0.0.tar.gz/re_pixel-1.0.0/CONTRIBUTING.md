# Contributing to Re-pixel

We love your input! We want to make contributing to Re-pixel as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## Pull Requests

Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/rakshithkalmadi/re-pixel.git
cd re-pixel

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=repixel --cov-report=html

# Run specific test file
python -m pytest tests/test_repixel.py -v
```

## Code Style

We use several tools to maintain code quality:

```bash
# Format code
black repixel/ tests/ examples/

# Check linting
flake8 repixel/ tests/ examples/

# Type checking
mypy repixel/
```

## Code Guidelines

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep line length under 88 characters (Black default)
- Use meaningful variable and function names

## Testing Guidelines

- Write tests for all new features and bug fixes
- Use descriptive test names that explain what is being tested
- Include both positive and negative test cases
- Test edge cases and error conditions
- Maintain test coverage above 80%

## Documentation

- Update README.md for any user-facing changes
- Add docstrings to all public functions and classes
- Include code examples in docstrings where helpful
- Update CHANGELOG.md with notable changes

## Submitting Issues

### Bug Reports

Great bug reports tend to have:

- A quick summary and/or background
- Steps to reproduce
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

### Feature Requests

We love feature requests! Please provide:

- A clear description of the feature
- Why you think it would be useful
- Examples of how it would be used
- Any implementation ideas you might have

## Any contributions you make will be under the MIT Software License

When you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## References

This document was adapted from the open-source contribution guidelines for [Facebook's Draft](https://github.com/facebook/draft-js/blob/a9316a723f9e918afde44dea68b5f9f39b7d9b00/CONTRIBUTING.md).
