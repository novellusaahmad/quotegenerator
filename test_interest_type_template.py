import pytest
from app import app

def test_interest_type_template():
    app.config['TESTING'] = True
    with app.test_client() as client:
        response = client.get('/api/scenario-comparison/templates/interest_types', query_string={
            'loan_type': 'bridge',
            'gross_amount': 1000000,
            'loan_term': 12,
            'property_value': 2000000
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        scenarios = data['scenarios']
        assert len(scenarios) == 4
        types = [s['parameters']['interest_type'] for s in scenarios]
        assert types == ['simple', 'compound_daily', 'compound_monthly', 'compound_quarterly']
