import pytest
import requests
from urllib.parse import urljoin

from tests.API_endpoints.constants import BASE_URL, MANAGER_LOGIN, MANAGER_PASSWORD, TEST_SUBSCRIBER_ID
from tests.API_endpoints.helpers import get_auth_token

def test_get_subscriber_tariff_200():
    token = get_auth_token({"login": MANAGER_LOGIN, "password": MANAGER_PASSWORD})
    
    url = urljoin(BASE_URL, f"/subscribers/{TEST_SUBSCRIBER_ID}/tariff")
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "tariff_name" in data
    assert isinstance(data["tariff_name"], str)
    assert len(data["tariff_name"].strip()) > 0
    assert response.elapsed.total_seconds() * 1000 < 500

def test_get_subscriber_tariff_400():
    token = get_auth_token({"login": MANAGER_LOGIN, "password": MANAGER_PASSWORD})
    
    url = urljoin(BASE_URL, f"/subscribers/{'any_value'}/tariff")
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    
    assert response.status_code == 400
    data = response.json()
    assert "tariff_name" in data
    assert isinstance(data["tariff_name"], str)
    assert len(data["tariff_name"].strip()) > 0
    assert response.elapsed.total_seconds() * 1000 < 500

test_get_subscriber_tariff_200()
test_get_subscriber_tariff_400()