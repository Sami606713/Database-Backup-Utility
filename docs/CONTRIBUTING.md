# Contributing to Database Backup Utility

## Development Setup

```bash
# Clone and install
git clone https://github.com/your-repo/database-backup-utility.git
cd database-backup-utility
uv sync --dev

# Install pre-commit hooks
uv run pre-commit install
```

---

## Project Structure

See [FOLDER_STRUCTURE.md](./FOLDER_STRUCTURE.md) for detailed explanation.

---

## Code Style

- **Formatter**: Black (line length: 100)
- **Linter**: Ruff
- **Type Hints**: Required for all public APIs
- **Docstrings**: Google style

```bash
# Format code
uv run black .

# Run linter
uv run ruff check .

# Type checking
uv run mypy db_backup/
```

---

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=db_backup --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_connectors.py -v
```

### Writing Tests

- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- Use fixtures from `tests/conftest.py`
- Mock external dependencies (DB connections, cloud storage)

---

## Adding a New Database Connector

1. Create `db_backup/connectors/newdb_connector.py`
2. Inherit from `BaseConnector`
3. Implement all abstract methods
4. Add tests in `tests/unit/test_connectors.py`
5. Update `DBType` enum in `constants.py`
6. Document in `USER_GUIDE.md`

---

## Adding a New Storage Backend

1. Create `db_backup/storage/newstorage.py`
2. Inherit from `BaseStorage`
3. Implement all abstract methods
4. Add tests in `tests/unit/test_storage.py`
5. Update `StorageType` enum
6. Document cloud setup in `USER_GUIDE.md`

---

## Pull Request Process

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes with tests
4. Run tests and linting
5. Commit with conventional commits: `feat: add X` / `fix: resolve Y`
6. Push and open PR against `main`
7. Wait for review

---

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add Azure Blob Storage support
fix: handle empty database backup gracefully
docs: update installation instructions
test: add MySQL connector tests
refactor: simplify backup manager logic
```
