# Contributing to Cashflow Radar

Thank you for your interest in contributing!

## Development Setup

```bash
# Clone the repository
git clone https://github.com/mozunking/cashflow-radar.git
cd cashflow-radar

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Start development environment
docker compose -f docker/compose.dev.yml up -d
```

## Branch Strategy

- `main`: Stable release
- `develop`: Integration branch
- `feature/*`: Feature development
- `fix/*`: Bug fixes
- `refactor/*`: Code refactoring

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes with clear commit messages
4. Push to your fork
5. Open a Pull Request against `develop`
6. Ensure CI passes
7. Request review from maintainers

## Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

## Code Review Checklist

- [ ] Code follows project style guidelines
- [ ] UT coverage ≥ 80%
- [ ] All tests pass
- [ ] No hardcoded secrets
- [ ] Documentation updated if needed
- [ ] No security vulnerabilities

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
