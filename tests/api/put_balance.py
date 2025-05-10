import pytest
import requests
from urllib.parse import urljoin

from tests.api.constants import BASE_URL, SUBSCRIBER_LOGIN, SUBSCRIBER_PASSWORD, TEST_SUBSCRIBER_ID
from tests.api.helpers import get_auth_token

def test_top_up_subscriber_balance_200():
    token = get_auth_token({"login": SUBSCRIBER_LOGIN, "password": SUBSCRIBER_PASSWORD})
    
    url = urljoin(BASE_URL, f"/subscribers/{TEST_SUBSCRIBER_ID}/balance")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "amount": 50.00,
        "payment_method": "wallet"
    }
    response = requests.post(url, headers=headers, json=payload)
    
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result.get("new_balance"), (int, float))
    assert response.elapsed.total_seconds() * 1000 < 500

def test_top_up_subscriber_balance_400():
    token = get_auth_token({"login": SUBSCRIBER_LOGIN, "password": SUBSCRIBER_PASSWORD})
    
    url = urljoin(BASE_URL, f"/subscribers/{TEST_SUBSCRIBER_ID}/balance")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "amount": -50.00,
        "payment_method": "wallet"
    }
    response = requests.post(url, headers=headers, json=payload)
    
    assert response.status_code == 400
    result = response.json()
    assert isinstance(result.get("new_balance"), (int, float))
    assert response.elapsed.total_seconds() * 1000 < 500

test_top_up_subscriber_balance_200()
test_top_up_subscriber_balance_400()    