import pytest
import requests
from urllib.parse import urljoin

from tests.API_endpoints.constants import BASE_URL, MANAGER_LOGIN, MANAGER_PASSWORD
from tests.API_endpoints.helpers import get_auth_token

def test_register_client_201():
    token = get_auth_token({"login": MANAGER_LOGIN, "password": MANAGER_PASSWORD})
    
    url = urljoin(BASE_URL, "/auth/registration")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "phone": "+79000000000",
        "full_name": "Test Client",
        "role": "client"
    }
    response = requests.post(url, headers=headers, json=payload)
    
    assert response.status_code == 201
    assert response.elapsed.total_seconds() * 1000 < 500

def test_register_client_400():
    token = get_auth_token({"login": MANAGER_LOGIN, "password": MANAGER_PASSWORD})
    
    url = urljoin(BASE_URL, "/auth/registration")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "phone": "abcd",
        "full_name": "Test Client",
        "role": "client"
    }
    response = requests.post(url, headers=headers, json=payload)
    
    assert response.status_code == 400
    assert response.elapsed.total_seconds() * 1000 < 500

test_register_client_201()
test_register_client_400()    