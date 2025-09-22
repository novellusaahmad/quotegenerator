import os
import json
import pytest

# Skip module if Flask app dependencies are missing
pytest.importorskip("flask")
pytest.importorskip("app")

from app import app
from flask import current_app
from snowflake_utils import SNOWFLAKE_CONFIG_FILE


def test_snowflake_config_persisted(tmp_path):
    """Saving Snowflake config should persist to disk and reload."""
    client = app.test_client()

    # Ensure clean state
    if os.path.exists(SNOWFLAKE_CONFIG_FILE):
        os.remove(SNOWFLAKE_CONFIG_FILE)

    payload = {
        'method': 'password',
        'user': 'u',
        'password': 'p',
        'account': 'acc'
    }
    res = client.post('/api/snowflake/config', json=payload)
    assert res.get_json()['success'] is True

    # File should now exist with same contents
    assert os.path.exists(SNOWFLAKE_CONFIG_FILE)
    with open(SNOWFLAKE_CONFIG_FILE) as f:
        data = json.load(f)
    assert data['account'] == 'acc'

    # Simulate new process by clearing config
    with app.app_context():
        current_app.config.pop('SNOWFLAKE_CONFIG', None)

    # GET should reload from file
    res = client.get('/api/snowflake/config')
    assert res.get_json()['config']['account'] == 'acc'

    # Delete config
    res = client.delete('/api/snowflake/config')
    assert res.get_json()['success'] is True
    assert not os.path.exists(SNOWFLAKE_CONFIG_FILE)
