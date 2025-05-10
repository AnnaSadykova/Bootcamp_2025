import pytest
import requests
from urllib.parse import urljoin

from tests.API_endpoints.constants import BASE_URL, MANAGER_LOGIN, MANAGER_PASSWORD, TEST_SUBSCRIBER_ID
from tests.API_endpoints.helpers import get_auth_token

def test_send_sms_notification_200():
    token = get_auth_token({"login": MANAGER_LOGIN, "password": MANAGER_PASSWORD})
    
    url = urljoin(BASE_URL, f"/notifications/{TEST_SUBSCRIBER_ID}")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "type": "limit_100"
    }
    response = requests.post(url, headers=headers, json=payload)
    
    assert response.status_code == 200
    assert response.elapsed.total_seconds() * 1000 < 500

def test_send_sms_notification_400():
    token = get_auth_token({"login": MANAGER_LOGIN, "password": MANAGER_PASSWORD})
    
    url = urljoin(BASE_URL, f"/notifications/{TEST_SUBSCRIBER_ID}")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "type": "limit_1000"
    }
    response = requests.post(url, headers=headers, json=payload)
    
    assert response.status_code == 400
    assert response.elapsed.total_seconds() * 1000 < 500

test_send_sms_notification_200()
test_send_sms_notification_400()    