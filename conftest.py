import os

# Use in-memory SQLite database for tests to avoid external dependencies
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
