import pytest
import requests
from urllib.parse import urljoin
from api.constants import BASE_URL, MANAGER_PASSWORD, TEST_SUBSCRIBER_ID, MANAGER_LOGIN, TEST_TARIFF_ID
from api.helpers import get_auth_token

def test_change_subscriber_tariff_200():
    token = get_auth_token({"login": MANAGER_LOGIN, "password": MANAGER_PASSWORD})
    
    url = urljoin(BASE_URL, f"/subscribers/{TEST_SUBSCRIBER_ID}/tariff")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "new_tariff_id": TEST_TARIFF_ID
    }
    response = requests.put(url, headers=headers, json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "tariff_name" in data
    assert isinstance(data["tariff_name"], str)
    assert len(data["tariff_name"].strip()) > 0
    assert response.elapsed.total_seconds() * 1000 < 500

def test_change_subscriber_tariff_400():
    token = get_auth_token({"login": MANAGER_LOGIN, "password": MANAGER_PASSWORD})
    
    url = urljoin(BASE_URL, f"/subscribers/{TEST_SUBSCRIBER_ID}/tariff")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "new_tariff_id": "wrong value"
    }
    response = requests.put(url, headers=headers, json=payload)
    
    assert response.status_code == 400
    data = response.json()
    assert "tariff_name" in data
    assert isinstance(data["tariff_name"], str)
    assert len(data["tariff_name"].strip()) > 0
    assert response.elapsed.total_seconds() * 1000 < 500

test_change_subscriber_tariff_200()
test_change_subscriber_tariff_400()