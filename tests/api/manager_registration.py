import pytest
import requests
from urllib.parse import urljoin

from tests.api.constants import ADMIN_LOGIN, ADMIN_PASSWORD, BASE_URL
from tests.api.helpers import get_auth_token

def test_register_manager_201():
    token = get_auth_token({"login": ADMIN_LOGIN, "password": ADMIN_PASSWORD})
    
    url = urljoin(BASE_URL, "/auth/registration")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "phone": "+79000000001",
        "full_name": "Test Manager",
        "role": "manager"
    }
    response = requests.post(url, headers=headers, json=payload)
    
    assert response.status_code == 201
    assert response.elapsed.total_seconds() * 1000 < 500

def test_register_manager_400():
    token = get_auth_token({"login": ADMIN_LOGIN, "password": ADMIN_PASSWORD})
    
    url = urljoin(BASE_URL, "/auth/registration")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "phone": "0000",
        "full_name": "Test Manager",
        "role": "manager"
    }
    response = requests.post(url, headers=headers, json=payload)
    
    assert response.status_code == 400
    assert response.elapsed.total_seconds() * 1000 < 500

test_register_manager_201()
test_register_manager_400()