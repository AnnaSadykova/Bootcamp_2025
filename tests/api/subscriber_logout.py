import pytest
import requests
from urllib.parse import urljoin
from tests.API_endpoints.constants import BASE_URL, SUBSCRIBER_LOGIN, SUBSCRIBER_PASSWORD, TEST_SUBSCRIBER_ID

from tests.API_endpoints.helpers import get_auth_token

def test_client_logout_200():
    token = get_auth_token({"login": SUBSCRIBER_LOGIN, "password": SUBSCRIBER_PASSWORD})
    
    url = urljoin(BASE_URL, f"/auth/logout/{TEST_SUBSCRIBER_ID}")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.post(url, headers=headers)
    
    assert response.status_code == 200
    assert response.elapsed.total_seconds() * 1000 < 500

def test_client_logout_400():
    token = get_auth_token({"login": SUBSCRIBER_LOGIN, "password": SUBSCRIBER_PASSWORD})
    
    url = urljoin(BASE_URL, f"/auth/logout/{'wrong value'}")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.post(url, headers=headers)
    
    assert response.status_code == 400
    assert response.elapsed.total_seconds() * 1000 < 500

test_client_logout_200()
test_client_logout_400()    