import pytest

pytest.importorskip("flask")

from app import app
import routes  # noqa: F401 ensure routes registered


def test_snowflake_config_and_logs(monkeypatch):
    client = app.test_client()
    app.config['SNOWFLAKE_SYNC_LOGS'] = []

    # Missing required parameters
    resp = client.post('/api/snowflake/config', json={'user': 'u'})
    assert resp.status_code == 400

    # Provide minimal valid configuration
    payload = {'user': 'u', 'password': 'p', 'account': 'a'}
    resp = client.post('/api/snowflake/config', json=payload)
    assert resp.status_code == 200
    assert resp.get_json()['success']

    # Patch sync function to avoid real Snowflake dependency
    def fake_sync(table, data):
        return None

    monkeypatch.setattr(routes, 'sync_data_to_snowflake', fake_sync)

    # Trigger a sync
    resp = client.post('/api/snowflake/sync', json={'table': 't', 'data': {'x': 1}})
    assert resp.status_code == 200
    assert resp.get_json()['success']

    # Retrieve logs
    logs_resp = client.get('/api/snowflake/logs')
    assert logs_resp.status_code == 200
    logs = logs_resp.get_json()['logs']
    assert any('Configured Snowflake connection' in entry for entry in logs)
    assert any('Synced' in entry for entry in logs)
