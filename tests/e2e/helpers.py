import os
import pytest
from datetime import datetime, timedelta
import requests

from tests.e2e.constants import BASE_URL, TEST_SUBSCRIBER_NAME, TEST_SUBSCRIBER_PASSWORD, TEST_SUBSCRIBER_PHONE, TEST_TARIFF_ID

@pytest.fixture
def test_subscriber():
    """Фикстура для создания тестового абонента"""
    # Регистрация абонента через API CRM
    reg_data = {
        "phone": TEST_SUBSCRIBER_PHONE,
        "full_name": TEST_SUBSCRIBER_NAME,
        "role": "client"
    }
    response = requests.post(f"{BASE_URL}/auth/registration", json=reg_data)
    assert response.status_code == 201
    
    # Установка дополнительного баланса
    # balance_data = {"amount": 100.0, "payment_method": "wallet"}
    # response = requests.post(
    #     f"{BASE_URL}/subscribers/{response.json()['subscriber_id']}/balance",
    #     json=balance_data
    # )
    # assert response.status_code == 200
    
    # Получение данных абонента
    subscriber_data = {
        "id": response.json()['subscriber_id'],
        "phone": TEST_SUBSCRIBER_PHONE,
        "balance": 100.0
    }
    return subscriber_data

@pytest.fixture
def auth_token(test_subscriber: dict[str, Any]):
    """Фикстура для получения токена авторизации"""
    auth_data = {
        "login": TEST_SUBSCRIBER_PHONE,
        "password": TEST_SUBSCRIBER_PASSWORD  # Предполагается стандартный пароль
    }
    response = requests.post(f"{BASE_URL}/auth", json=auth_data)
    assert response.status_code == 200
    return response.json()['access_token']

def set_tariff(subscriber_id, tariff_name):
    """Установка тарифа для абонента"""
    # В реальной реализации нужно получить tariff_id по имени
    tariff_id = TEST_TARIFF_ID  # Здесь должен быть реальный UUID тарифа
    response = requests.put(
        f"{BASE_URL}/subscribers/{subscriber_id}/tariff",
        json={"new_tariff_id": tariff_id},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    return response.json()

def make_call(subscriber_id, call_type, contact_number, duration_minutes, auth_token):
    """Эмуляция звонка с созданием CDR-файла в формате:
    01,79000000000,79900000001,2025-06-01T23:59:55,2025-06-02T00:00:00
    """
    # Создаем временную папку для CDR-файлов, если ее нет
    os.makedirs("files", exist_ok=True)
    
    # Генерируем временные метки
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    # Формируем имя файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cdr_filename = f"files/CDR_{TEST_SUBSCRIBER_PHONE}_{timestamp}.txt"
    
    # Создаем содержимое файла в нужном формате
    cdr_content = f"{call_type},{TEST_SUBSCRIBER_PHONE},{contact_number},{start_time.isoformat()},{end_time.isoformat()}"
    
    # Записываем файл
    with open(cdr_filename, 'w') as f:
        f.write(cdr_content)
    
    # Отправляем файл на обработку
    with open(cdr_filename, 'rb') as f:
        files = {'file': (cdr_filename, f, 'text/plain')}
        response = requests.post(
            f"{BASE_URL}/cdr/process",
            files=files,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    # Удаляем временный файл после отправки
    try:
        os.remove(cdr_filename)
    except OSError:
        pass
    
    assert response.status_code == 200
    return response.json()


def get_balance(subscriber_id):
    """Получение текущего баланса"""
    response = requests.get(
        f"{BASE_URL}/subscribers/{subscriber_id}/balance",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    return float(response.json()['balance'])

def check_billing_transaction(subscriber_id, call_id, expected_amount):
    """Проверка корректности транзакции"""
    response = requests.get(
        f"{BASE_URL}/billing/transactions?subscriber_id={subscriber_id}&call_id={call_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) == 1
    assert float(transactions[0]['amount']) == expected_amount
    return transactions[0]

def check_hrs_usage(subscriber_id, expected_outgoing=0, expected_incoming=0):
    """Проверка учета минут в HRS"""
    response = requests.get(
        f"{BASE_URL}/hrs/usage?subscriber_id={subscriber_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    usage_data = response.json()
    if expected_outgoing is not None:
        assert usage_data['outgoing_minutes'] >= expected_outgoing
    if expected_incoming is not None:
        assert usage_data['incoming_minutes'] >= expected_incoming
    return usage_data