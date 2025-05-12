import os
import allure
import pytest
from tests.cdr.helpers import validate_cdr_file

@pytest.fixture
def test_files_dir():
    return os.path.join(os.path.dirname(__file__), 'files')

@allure.story("Позитивный сценарий")
@allure.title("Валидный CDR-файл")
@allure.severity(allure.severity_level.CRITICAL)
def test_positive_case(test_files_dir):
    """Test file with no errors"""
    errors = validate_cdr_file(os.path.join(test_files_dir, 'CDR_positive.txt'))
    assert not any(errors.values()), "Нет ошибок в позитивном сценарии"
    
@allure.story("Негативный сценарий")
@allure.title("Пустой CDR-файл")
@allure.severity(allure.severity_level.NORMAL)
def test_empty_file(test_files_dir):
    """Test empty file validation"""
    errors = validate_cdr_file(os.path.join(test_files_dir, 'CDR_negative_empty_file.txt'))
    assert "Файл пустой" in errors["file_structure"]

@allure.story("Негативный сценарий")
@allure.title("Менее 10 записей в CDR-файле")
@allure.severity(allure.severity_level.NORMAL)
def test_incorrect_record_count_less(test_files_dir):
    """Test file with less than 10 records"""
    errors = validate_cdr_file(os.path.join(test_files_dir, 'CDR_negative_9.txt'))
    assert isinstance(errors["file_structure"][0], int), "Ожидалось целое число"
    assert errors["file_structure"][0] < 10, "Количество записей < 10"

@allure.story("Негативный сценарий")
@allure.title("Более 10 записей в CDR-файле")
@allure.severity(allure.severity_level.CRITICAL)
def test_incorrect_record_count_more(test_files_dir):
    """Test file with more than 10 records"""
    errors = validate_cdr_file(os.path.join(test_files_dir, 'CDR_negative_11.txt'))
    assert isinstance(errors["file_structure"][0], int), "Ожидалось целое число"
    assert errors["file_structure"][0] > 10, "Количество записей > 10"

@allure.story("Негативный сценарий")
@allure.title("Нет разделителя (запятой) между полями = неверное количество полей")
@allure.severity(allure.severity_level.CRITICAL)
def test_missing_comma(test_files_dir):
    """Test file with missing comma in records"""
    errors = validate_cdr_file(os.path.join(test_files_dir, 'CDR_negative_without_comma.txt'))
    assert errors["record_format"][0] != 5

@allure.story("Негативный сценарий")
@allure.title("Нет номера телефона")
@allure.severity(allure.severity_level.CRITICAL)
def test_empty_parameter(test_files_dir):
    """Test file with empty parameter in record"""
    
    errors = validate_cdr_file(os.path.join(test_files_dir, 'CDR_negative_empty_parameter.txt'))
    assert "Номер телефона отсутствует" in errors["phone_numbers"][0]

@allure.story("Негативный сценарий")
@allure.title("Длина номера телефона больше 11")
@allure.severity(allure.severity_level.CRITICAL)
def test_invalid_phone_number(test_files_dir):
    """Test file with invalid phone number (wrong length)"""
    errors = validate_cdr_file(os.path.join(test_files_dir, 'CDR_negative_number12.txt'))
    assert errors["phone_numbers"][0] != 11

@allure.story("Негативный сценарий")
@allure.title("Тип вызова не 01 или не 02")
@allure.severity(allure.severity_level.CRITICAL)
def test_invalid_call_type(test_files_dir):
    """Test file with invalid call type"""
    errors = validate_cdr_file(os.path.join(test_files_dir, 'CDR_negative_03.txt'))
    assert "Неподдерживаемый тип вызова '03'" in errors["record_format"][0]

@allure.story("Негативный сценарий")
@allure.title("Нет хронологии записей в CDR-файле")
@allure.severity(allure.severity_level.NORMAL)
def test_time_sequence_error(test_files_dir):
    """Test file with records not in chronological order"""
    errors = validate_cdr_file(os.path.join(test_files_dir, 'CDR_negative_without_timeOrder.txt'))
    assert errors["time_sequence"], "Хронологический порядок записей отсутствует"

@allure.story("Негативный сценарий")
@allure.title("Время окончания звонка наступило раньше времени начала звонка")
@allure.severity(allure.severity_level.CRITICAL)
def test_timeline_error(test_files_dir):
    """Test file with timeline errors"""
    errors = validate_cdr_file(os.path.join(test_files_dir, 'CDR_negative_without_timelineOrder.txt'))
    assert errors["timestamps"], "Время окончания звонка наступило раньше времени начала звонка"

@allure.story("Негативный сценарий")
@allure.title("Один абонент звонит одновременно 2-м абонентам")
@allure.severity(allure.severity_level.CRITICAL)
def test_simultaneous_outgoing_calls(test_files_dir):
    """Test file with simultaneous outgoing calls"""
    errors = validate_cdr_file(os.path.join(test_files_dir, 'CDR_negative_2OutgoingCallsSimultaneously.txt'))
    assert "Конфликт исходящих вызовов" in errors["call_logic"][0]

@allure.story("Негативный сценарий")
@allure.title("2 абонента звонят одновременно 1-му абоненту")
@allure.severity(allure.severity_level.CRITICAL)
def test_simultaneous_incoming_calls(test_files_dir):
    """Test file with simultaneous incoming calls"""
    errors = validate_cdr_file(os.path.join(test_files_dir, 'CDR_negative_2IncomingCallsSimultaneously.txt'))
    assert "Конфликт входящих вызовов" in errors["call_logic"][0]

@allure.story("Негативный сценарий")
@allure.title("SQL-инъекция в поле")
@allure.severity(allure.severity_level.CRITICAL)
def test_sql_injection(test_files_dir):
    """Test file with possible SQL injection"""
    errors = validate_cdr_file(os.path.join(test_files_dir, 'CDR_negative_injection.txt'))
    assert "SQL-инъекция" in errors["security"][0]

@allure.story("Негативный сценарий")
@allure.title("Звонок пересекает полночь и не делится на 2 звонка")
@allure.severity(allure.severity_level.CRITICAL)
def test_midnight_crossing(test_files_dir):
    """Test file with call crossing midnight"""
    errors = validate_cdr_file(os.path.join(test_files_dir, 'CDR_negative_without_2Records.txt'))
    assert "Звонок пересекает полночь и не делится на 2 звонка" in errors["midnight_crossing"][0]

@allure.story("Негативный сценарий")
@allure.title("Неверный код оператора")
@allure.severity(allure.severity_level.CRITICAL)
def test_wrong_operator_code(test_files_dir):
    """Test file with wrong operator code (not 900)"""
    errors = validate_cdr_file(os.path.join(test_files_dir, 'СDR_negative_otherOperator.txt'))
    assert "Неверный код оператора" in errors["operator_code"][0]