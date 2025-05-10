import pytest
import requests
from urllib.parse import urljoin

from tests.api.constants import BASE_URL, SUBSCRIBER_PASSWORD, SUBSCRIBER_LOGIN, MANAGER_PASSWORD, MANAGER_LOGIN

def get_subscriber_auth_token_200():
    url = urljoin(BASE_URL, "/auth")
    response = requests.post(url, json={"password": SUBSCRIBER_PASSWORD, "login": SUBSCRIBER_LOGIN})
    assert response.status_code == 200
    # TODO проверить роль из декодированного JWT токена, если роль там будет обозначена
    return response.json()["access_token"]

def get_subscriber_auth_token_400():
    url = urljoin(BASE_URL, "/auth")
    response = requests.post(url, json={"password": "wrong_password", "login": SUBSCRIBER_LOGIN})
    assert response.status_code == 400
    return response.json()["access_token"]

def get_manager_auth_token_200():
    url = urljoin(BASE_URL, "/auth")
    response = requests.post(url, json={"password": MANAGER_PASSWORD, "login": MANAGER_LOGIN})
    assert response.status_code == 200
    # TODO проверить роль из декодированного JWT токена, если роль там будет обозначена
    return response.json()["access_token"]

def get_manager_auth_token_400():
    url = urljoin(BASE_URL, "/auth")
    response = requests.post(url, json={"password": "wrong_password", "login": MANAGER_LOGIN})
    assert response.status_code == 400
    return response.json()["access_token"]

get_subscriber_auth_token_200()
get_subscriber_auth_token_400()
get_manager_auth_token_200()
get_manager_auth_token_400()