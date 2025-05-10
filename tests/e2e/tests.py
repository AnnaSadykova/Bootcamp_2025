import pytest
import requests

from tests.e2e.constants import BASE_URL, TEST_TARIFF_CLASSIC, TEST_TARIFF_MONTHLY
from tests.e2e.helpers import check_billing_transaction, check_hrs_usage, get_balance, make_call, set_tariff


# Основные тестовые случаи
def test_ucbrt1_1_outgoing_to_romashka_classic(test_subscriber, auth_token):
    """UCBRT1-1: Исходящий звонок абоненту Ромашки по тарифу Классика"""
    set_tariff(test_subscriber['id'], TEST_TARIFF_CLASSIC, auth_token)
    call_info = make_call(test_subscriber['id'], "01", "79123456780", 10, is_romashka=True)
    
    # Проверка: 1.5 у.е./мин * 10 мин = 15 у.е.
    assert get_balance(test_subscriber['id'], auth_token) == pytest.approx(85.0, 0.01)
    check_billing_transaction(test_subscriber['id'], call_info['call_id'], 15.0)
    check_hrs_usage(test_subscriber['id'], expected_outgoing=10)

def test_ucbrt1_2_incoming_from_romashka_classic(test_subscriber, auth_token):
    """UCBRT1-2: Входящий звонок от абонента Ромашки по тарифу Классика"""
    set_tariff(test_subscriber['id'], TEST_TARIFF_CLASSIC, auth_token)
    call_info = make_call(test_subscriber['id'], "02", "79123456780", 10, is_romashka=True)
    
    # Входящие звонки бесплатные
    assert get_balance(test_subscriber['id'], auth_token) == pytest.approx(100.0, 0.01)
    check_billing_transaction(test_subscriber['id'], call_info['call_id'], 0.0)
    check_hrs_usage(test_subscriber['id'], expected_incoming=10)

def test_ucbrt1_3_incoming_from_other_operator_classic(test_subscriber, auth_token):
    """UCBRT1-3: Входящий звонок от другого оператора по тарифу Классика"""
    set_tariff(test_subscriber['id'], TEST_TARIFF_CLASSIC, auth_token)
    call_info = make_call(test_subscriber['id'], "02", "79213456789", 10)
    
    # Входящие звонки бесплатные
    assert get_balance(test_subscriber['id'], auth_token) == pytest.approx(100.0, 0.01)
    check_billing_transaction(test_subscriber['id'], call_info['call_id'], 0.0)
    check_hrs_usage(test_subscriber['id'], expected_incoming=10)

def test_ucbrt1_4_outgoing_to_other_operator_classic(test_subscriber, auth_token):
    """UCBRT1-4: Исходящий звонок другому оператору по тарифу Классика"""
    set_tariff(test_subscriber['id'], TEST_TARIFF_CLASSIC, auth_token)
    call_info = make_call(test_subscriber['id'], "01", "79213456789", 10)
    
    # Проверка: 2.5 у.е./мин * 10 мин = 25 у.е.
    assert get_balance(test_subscriber['id'], auth_token) == pytest.approx(75.0, 0.01)
    check_billing_transaction(test_subscriber['id'], call_info['call_id'], 25.0)
    check_hrs_usage(test_subscriber['id'], expected_outgoing=10)

def test_ucbrt1_5_outgoing_to_other_operator_monthly_over_limit(test_subscriber, auth_token):
    """UCBRT1-5: Исходящий звонок другому оператору по тарифу Помесячный (>50 мин)"""
    set_tariff(test_subscriber['id'], TEST_TARIFF_MONTHLY, auth_token)
    call_info = make_call(test_subscriber['id'], "01", "79213456789", 52)
    
    # Первые 50 мин включены в тариф, 2 мин по 2.5 у.е.
    expected_balance = 100.0 - 100.0 - (2 * 2.5)  # -5.0
    assert get_balance(test_subscriber['id'], auth_token) == pytest.approx(expected_balance, 0.01)
    check_billing_transaction(test_subscriber['id'], call_info['call_id'], 5.0)
    
    # Проверка учета минут сверх лимита
    usage_data = check_hrs_usage(test_subscriber['id'], expected_outgoing=52)
    assert usage_data['outgoing_minutes_over_limit'] >= 2

def test_ucbrt1_6_outgoing_to_romashka_monthly_over_limit(test_subscriber, auth_token):
    """UCBRT1-6: Исходящий звонок Ромашке по тарифу Помесячный (>50 мин)"""
    set_tariff(test_subscriber['id'], TEST_TARIFF_MONTHLY, auth_token)
    call_info = make_call(test_subscriber['id'], "01", "79123456780", 52, is_romashka=True)
    
    # Первые 50 мин включены в тариф, 2 мин по 1.5 у.е.
    expected_balance = 100.0 - 100.0 - (2 * 1.5)  # -3.0
    assert get_balance(test_subscriber['id'], auth_token) == pytest.approx(expected_balance, 0.01)
    check_billing_transaction(test_subscriber['id'], call_info['call_id'], 3.0)
    
    usage_data = check_hrs_usage(test_subscriber['id'], expected_outgoing=52)
    assert usage_data['outgoing_minutes_over_limit'] >= 2

def test_ucbrt1_7_incoming_from_other_operator_monthly_over_limit(test_subscriber, auth_token):
    """UCBRT1-7: Входящий звонок от другого оператора по тарифу Помесячный (>50 мин)"""
    set_tariff(test_subscriber['id'], TEST_TARIFF_MONTHLY, auth_token)
    call_info = make_call(test_subscriber['id'], "02", "79213456789", 52)
    
    # Входящие звонки бесплатные, даже сверх лимита
    assert get_balance(test_subscriber['id'], auth_token) == pytest.approx(0.0, 0.01)  # Только месячная плата
    check_billing_transaction(test_subscriber['id'], call_info['call_id'], 0.0)
    check_hrs_usage(test_subscriber['id'], expected_incoming=52)

def test_ucbrt1_8_incoming_from_romashka_monthly_over_limit(test_subscriber, auth_token):
    """UCBRT1-8: Входящий звонок от Ромашки по тарифу Помесячный (>50 мин)"""
    set_tariff(test_subscriber['id'], TEST_TARIFF_MONTHLY, auth_token)
    call_info = make_call(test_subscriber['id'], "02", "79123456780", 52, is_romashka=True)
    
    # Входящие звонки бесплатные
    assert get_balance(test_subscriber['id'], auth_token) == pytest.approx(0.0, 0.01)  # Только месячная плата
    check_billing_transaction(test_subscriber['id'], call_info['call_id'], 0.0)
    check_hrs_usage(test_subscriber['id'], expected_incoming=52)
