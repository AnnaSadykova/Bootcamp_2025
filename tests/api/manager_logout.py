import pytest
import requests
from urllib.parse import urljoin
from tests.api.constants import BASE_URL, MANAGER_LOGIN, MANAGER_PASSWORD, TEST_SUBSCRIBER_ID

from tests.api.helpers import get_auth_token

def test_manager_logout_200():
    token = get_auth_token({"login": MANAGER_LOGIN, "password": MANAGER_PASSWORD})
    
    url = urljoin(BASE_URL, f"/auth/logout/{TEST_SUBSCRIBER_ID}")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.post(url, headers=headers)
    
    assert response.status_code == 200
    assert response.elapsed.total_seconds() * 1000 < 500

def test_manager_logout_400():
    token = get_auth_token({"login": MANAGER_LOGIN, "password": MANAGER_PASSWORD})
    
    url = urljoin(BASE_URL, f"/auth/logout/{'wrong value'}")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.post(url, headers=headers)
    
    assert response.status_code == 400
    assert response.elapsed.total_seconds() * 1000 < 500

test_manager_logout_200()
test_manager_logout_400()