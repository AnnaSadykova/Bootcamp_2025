import pytest
import requests
from urllib.parse import urljoin

from tests.api.constants import BASE_URL, MANAGER_LOGIN, MANAGER_PASSWORD, SUBSCRIBER_LOGIN, SUBSCRIBER_PASSWORD, TEST_SUBSCRIBER_ID
from tests.api.helpers import get_auth_token

def test_get_subscriber_balance_by_manager_200():
    token = get_auth_token({"login": MANAGER_LOGIN, "password": MANAGER_PASSWORD})
    
    url = urljoin(BASE_URL, f"/subscribers/{TEST_SUBSCRIBER_ID}/balance")
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    
    assert response.status_code == 200
    balance = response.json().get("balance")
    assert isinstance(balance, (int, float))
    assert response.elapsed.total_seconds() * 1000 < 500

def test_get_subscriber_balance_by_manager_400():
    token = get_auth_token({"login": MANAGER_LOGIN, "password": MANAGER_PASSWORD})
    
    url = urljoin(BASE_URL, f"/subscribers/{'any_value'}/balance")
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    
    assert response.status_code == 400
    balance = response.json().get("balance")
    assert isinstance(balance, (int, float))
    assert response.elapsed.total_seconds() * 1000 < 500

def test_get_subscriber_balance_by_subscriber_200():
    token = get_auth_token({"login": SUBSCRIBER_LOGIN, "password": SUBSCRIBER_PASSWORD})
    
    url = urljoin(BASE_URL, f"/subscribers/{TEST_SUBSCRIBER_ID}/balance")
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    
    assert response.status_code == 200
    balance = response.json().get("balance")
    assert isinstance(balance, (int, float))
    assert response.elapsed.total_seconds() * 1000 < 500

def test_get_subscriber_balance_by_subscriber_400():
    token = get_auth_token({"login": SUBSCRIBER_LOGIN, "password": SUBSCRIBER_PASSWORD})
    
    url = urljoin(BASE_URL, f"/subscribers/{'wrong_id'}/balance")
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    
    assert response.status_code == 400
    balance = response.json().get("balance")
    assert isinstance(balance, (int, float))
    assert response.elapsed.total_seconds() * 1000 < 500

test_get_subscriber_balance_by_manager_200()
test_get_subscriber_balance_by_manager_400()
test_get_subscriber_balance_by_subscriber_200()
test_get_subscriber_balance_by_subscriber_400()