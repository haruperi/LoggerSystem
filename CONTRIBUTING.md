# Contributing to MyLogger

Thank you for your interest in contributing to MyLogger!

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mylogger.git
cd mylogger
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest
```

With coverage:
```bash
pytest --cov=mylogger --cov-report=html
```

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Run black: `black mylogger tests`
- Run mypy: `mypy mylogger`

## Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Ensure all tests pass
6. Submit a pull request

## Questions?

Open an issue or discussion on GitHub.
