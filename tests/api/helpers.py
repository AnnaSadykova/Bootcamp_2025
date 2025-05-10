import requests
from urllib.parse import urljoin

from api.constants import BASE_URL

def get_auth_token(credentials):
    url = urljoin(BASE_URL, "/auth")
    response = requests.post(url, json=credentials)
    return response.json()["access_token"]