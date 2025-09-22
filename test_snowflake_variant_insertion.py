import json
import pytest

pytest.importorskip("flask")

import snowflake_utils


class DummyCursor:
    def __init__(self, executed):
        self.executed = executed

    def execute(self, stmt, params):  # pragma: no cover - executed in test
        self.executed.append((stmt, params))

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

    data = {"input_data": {"a": 1}, "value": 2}
    snowflake_utils.sync_data_to_snowflake("tbl", data)


    stmt, params = executed[0]
    assert stmt == "insert into tbl (input_data, value) select parse_json(%s), parse_json(%s)"
    assert params[0] == json.dumps({"a": 1})
    assert params[1] == json.dumps(2)


def test_sync_data_to_snowflake_handles_plain_strings(monkeypatch):
    executed = []

    monkeypatch.setattr(
        snowflake_utils, "_get_snowflake_connection", lambda: DummyConnection(executed)
    )
    monkeypatch.setattr(snowflake_utils, "ensure_snowflake_table", lambda *_, **__: None)

    data = {"loan_name": "asadahmad"}
    snowflake_utils.sync_data_to_snowflake("tbl", data)

    stmt, params = executed[0]
    assert stmt == "insert into tbl (loan_name) select parse_json(%s)"
    # The plain string should be JSON encoded so ``parse_json`` can handle it
    assert params[0] == json.dumps("asadahmad")


