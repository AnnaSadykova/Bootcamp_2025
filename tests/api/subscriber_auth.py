import pytest
import requests
from urllib.parse import urljoin

from tests.api.constants import BASE_URL, SUBSCRIBER_LOGIN, SUBSCRIBER_PASSWORD

def test_client_authentication_200():
    url = urljoin(BASE_URL, "/auth")
    payload = {
        "login": SUBSCRIBER_LOGIN,
        "password": SUBSCRIBER_PASSWORD
    }
    response = requests.post(url, json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert len(data["access_token"]) >= 10
    assert len(data["refresh_token"]) >= 10
    assert response.elapsed.total_seconds() * 1000 < 500

def test_client_authentication_400():
    url = urljoin(BASE_URL, "/auth")
    payload = {
        "login": SUBSCRIBER_LOGIN,
        "password": "wrong value"
    }
    response = requests.post(url, json=payload)
    
    assert response.status_code == 400
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert len(data["access_token"]) >= 10
    assert len(data["refresh_token"]) >= 10
    assert response.elapsed.total_seconds() * 1000 < 500

test_client_authentication_200()
test_client_authentication_400()