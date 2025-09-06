import json
import pytest

pytest.importorskip("flask")

import snowflake_utils


class DummyCursor:
    def __init__(self, executed):
        self.executed = executed

    def execute(self, stmt, params):  # pragma: no cover - executed in test
        self.executed.append(params)

    def close(self):
        pass


class DummyConnection:
    def __init__(self, executed):
        self.executed = executed

    def cursor(self):
        return DummyCursor(self.executed)

    def commit(self):
        pass

    def close(self):
        pass


def test_sync_data_to_snowflake_parses_json(monkeypatch):
    executed = []

    monkeypatch.setattr(
        snowflake_utils, "_get_snowflake_connection", lambda: DummyConnection(executed)
    )
    monkeypatch.setattr(snowflake_utils, "ensure_snowflake_table", lambda *_, **__: None)

    data = {"input_data": json.dumps({"a": 1}), "value": 2}
    snowflake_utils.sync_data_to_snowflake("tbl", data)

    assert executed[0][0] == {"a": 1}
    assert executed[0][1] == 2

