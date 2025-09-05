import pytest
from app import app


def test_scenario_comparison_session_size():
    app.config['TESTING'] = True
    with app.test_client() as client:
        payload = {
            "scenarios": [
                {
                    "name": "Scenario 1",
                    "parameters": {
                        "loan_type": "bridge",
                        "gross_amount": 100000,
                        "loan_term": 12,
                        "interest_rate": 0.05
                    }
                }
            ]
        }
        response = client.post('/api/scenario-comparison/create', json=payload)
        assert response.status_code == 200
        with client.session_transaction() as sess:
            assert 'scenario_comparison_id' in sess
            assert 'scenario_comparison' not in sess
        cookie_name = app.config.get('SESSION_COOKIE_NAME', 'session')
        cookie = next((c for c in client.cookie_jar if c.name == cookie_name), None)
        assert cookie is not None
        assert len(cookie.value) < 4093
