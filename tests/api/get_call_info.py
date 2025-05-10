import pytest
import requests
from urllib.parse import urljoin

from tests.API_endpoints.constants import BASE_URL, MANAGER_LOGIN, MANAGER_PASSWORD, TEST_CALL_ID
from tests.API_endpoints.helpers import get_auth_token

def test_get_call_info_200():
    token = get_auth_token({"login": MANAGER_LOGIN, "password": MANAGER_PASSWORD})
    
    url = urljoin(BASE_URL, f"/calls/{TEST_CALL_ID}")
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    
    assert response.status_code == 200
    assert len(response.content) > 0
    assert response.elapsed.total_seconds() * 1000 < 500

def test_get_call_info_400():
    token = get_auth_token({"login": MANAGER_LOGIN, "password": MANAGER_PASSWORD})
    
    url = urljoin(BASE_URL, f"/calls/{'wrong value'}")
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    
    assert response.status_code == 400
    assert len(response.content) > 0
    assert response.elapsed.total_seconds() * 1000 < 500

test_get_call_info_200()
test_get_call_info_400()