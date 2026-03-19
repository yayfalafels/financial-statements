# Test Mock Databases

**Purpose**: Physical SQLite databases for SIT (System Integration Testing)

**Directory**: `tests/.test_data/`

**Status**: This directory is tracked in git. Only generated SQLite artifacts are gitignored (`*.db`, `*-journal.db`, `*-shm.db`, `*-wal.db`).

---

## Mock Databases

### mock_homebudget.db

**Purpose**: Simulates real HomeBudget database for testing adapters and reconciliation logic

**Schema Source**: HomeBudget application database schema

**Data Source**: `tests/fixtures/transactions.json`

**Contents**:
- Accounts table (wallets, investment accounts, credit accounts)
- Categories table (income and expense categories with hierarchy)
- Transactions table (synthetic transactions for test period)
- Tags, payees, and other HomeBudget metadata

**Lifecycle**: Recreated at test session start, reset to baseline between test functions

### mock_app.db

**Purpose**: Application SQLite database for financial statements app

**Schema Source**: `src/python/closing/storage/schema.sql`

**Contents**:
- Financial statement snapshots
- Session management tables
- Reconciliation decision log
- Exchange rate cache
- Account mappings

**Lifecycle**: Recreated at test session start, reset to baseline between test functions

---

## Database Initialization

Databases are automatically created by pytest fixtures in `tests/conftest.py`:

```python
@pytest.fixture(scope="session", autouse=True)
def setup_test_databases():
    """Initialize mock databases at session start."""
    # Creates databases and loads fixtures
```

---

## Inspecting Databases

### Using SQLite CLI

```bash
# Open mock HomeBudget database
sqlite3 tests/.test_data/mock_homebudget.db

# Example queries
.tables
.schema transactions
SELECT * FROM accounts;
SELECT COUNT(*) FROM transactions;
```

### Using DB Browser for SQLite

1. Download from https://sqlitebrowser.org/
2. Open `tests/.test_data/mock_homebudget.db`
3. Browse tables, run queries, inspect schema

### Using Python

```python
import sqlite3

conn = sqlite3.connect("tests/.test_data/mock_homebudget.db")
cursor = conn.cursor()

# Query accounts
cursor.execute("SELECT name, type, currency FROM accounts")
for row in cursor.fetchall():
    print(row)

conn.close()
```

---

## Resetting Databases

### Automatic Reset

Databases are automatically reset between test functions to ensure isolation:

```python
@pytest.fixture(scope="function")
def mock_homebudget_db():
    """Reset database to baseline state."""
    db_path = Path(__file__).parent / ".test_data" / "mock_homebudget.db"
    reset_database_to_fixtures(db_path)
    return str(db_path)
```

### Manual Reset

Delete the `.test_data/` directory to force complete rebuild:

```bash
# Windows PowerShell
Remove-Item -Recurse -Force tests\.test_data

# Next pytest run will recreate databases
pytest tests/unit/
```

---

## Fixture Data

Baseline data loaded into mock databases comes from:

- **Accounts**: `tests/fixtures/accounts.json`
- **Categories**: `tests/fixtures/categories.json`
- **Transactions**: `tests/fixtures/transactions.json`

To update mock database contents:
1. Edit fixture JSON files
2. Delete `.test_data/` directory
3. Run pytest to recreate with new fixtures

---

## Troubleshooting

### Database locked error

If you see "database is locked" errors:

1. Close any SQLite browser tools
2. Kill any hanging test processes
3. Delete `.test_data/` and rerun tests

### Fixture data mismatch

If tests expect data that doesn't exist in mock database:

1. Check `tests/fixtures/*.json` for expected data
2. Verify database initialization in `tests/conftest.py`
3. Delete `.test_data/` to force rebuild from fixtures

### Database schema mismatch

If tests fail with column or table not found errors:

1. Check if HomeBudget schema changed
2. Update schema initialization in `tests/conftest.py`
3. Delete `.test_data/` to recreate with new schema

---

## Best Practices

1. **Commit docs/configs, not generated DB artifacts** — Keep `README.md`, generators, and schema/config JSON tracked
2. **Don't modify databases manually** — Use fixtures to define test data
3. **Inspect after test failures** — Databases persist for debugging
4. **Clean rebuild if uncertain** — Delete `.test_data/` when in doubt
5. **Keep fixtures minimal** — Only include data needed for tests

---

## Version History

- **2026-03-08**: Initial mock database structure documented
