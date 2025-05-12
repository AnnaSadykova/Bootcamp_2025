import os
from datetime import datetime, time
from typing import List, Dict, Tuple
import re

def validate_cdr_file(file_path: str) -> Dict[str, List[str]]:
    """
    Валидирует CDR файл и возвращает список найденных ошибок с описанием.
    
    Args:
        file_path (str): Путь к CDR файлу для валидации
        
    Returns:
        Dict[str, List[str]]: Словарь с категориями ошибок и их описаниями
    """
    errors = {
        "file_structure": [],
        "record_format": [],
        "phone_numbers": [],
        "timestamps": [],
        "call_logic": [],
        "security": [],
        "time_sequence": [],
        "midnight_crossing": [],
        "operator_code": []
    }
    
    # Проверка существования файла
    if not os.path.exists(file_path):
        errors["file_structure"].append("Файл не существует")
        return errors
    
    # Проверка размера файла
    if os.path.getsize(file_path) == 0:
        errors["file_structure"].append("Файл пустой")
        return errors
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Проверка количества записей
    if len(lines) < 10:
        errors["file_structure"].append(len(lines))
    elif len(lines) > 10:
        errors["file_structure"].append(len(lines))
    
    # Проверка каждой записи
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            errors["record_format"].append(f"Строка {i}: Пустая строка")
            continue
            
        parts = [part.strip() for part in line.split(',')]
        
        # Проверка количества полей в записи
        if len(parts) != 5:
            errors["record_format"].append(len(parts))
            print( f"Строка {i}: Неправильное количество полей ({len(parts)} вместо 5)")
            continue
        
        call_type, subscriber, contact, start_time, end_time = parts

        # Проверка кода оператора для первого номера (subscriber)
        if len(subscriber) >= 4:  # Минимум 4 цифры (7 + код оператора)
            operator_code = subscriber[1:4]  # Вторая, третья и четвертая цифры
            if operator_code != '900':
                errors["operator_code"].append(
                    f"Строка {i}: Неверный код оператора '{operator_code}' "
                    f"в номере {subscriber}. Ожидается код '900'"
                )
        
        # Проверка типа вызова
        if call_type not in ('01', '02'):
            errors["record_format"].append(
                f"Строка {i}: Неподдерживаемый тип вызова '{call_type}' (допустимо: 01 или 02)"
            )
        
        # Проверка номеров телефонов
        phone_errors = []
        for field, number in [('subscriber', subscriber), ('contact', contact)]:
            if not number:
                phone_errors.append("Номер телефона отсутствует")
            else:
                if not number.isdigit():
                    phone_errors.append("Номер содержит нецифровые символы")
                if len(number) != 11:
                    phone_errors.append(len(number))

        if phone_errors:
            errors["phone_numbers"].append(phone_errors)
            print(f"Строка {i}: " + "; ".join(str(phone_errors)))
        
        # Проверка временных меток
        time_errors = []
        try:
            start_dt = datetime.fromisoformat(start_time)
        except ValueError:
            time_errors.append(f"Некорректный формат времени начала '{start_time}'")
        
        try:
            end_dt = datetime.fromisoformat(end_time)
        except ValueError:
            time_errors.append(f"Некорректный формат времени окончания '{end_time}'")
        
        if not time_errors and 'start_dt' in locals() and 'end_dt' in locals():
            if end_dt < start_dt:
                time_errors.append(f"Время окончания ({end_time}) раньше времени начала ({start_time})")
            if (end_dt - start_dt).total_seconds() < 1:
                time_errors.append("Длительность звонка менее 1 секунды")
        
        if time_errors:
            errors["timestamps"].append(f"Строка {i}: " + "; ".join(time_errors))
        
        # Проверка на SQL-инъекции
        sql_keywords = ['select', 'insert', 'update', 'delete', 'drop', 'alter', 'create']
        for part in parts:
            if any(keyword in part.lower() for keyword in sql_keywords):
                errors["security"].append(f"Строка {i}: Обнаружена возможная SQL-инъекция в поле '{part}'")
                break
    
    # Дополнительные проверки логики звонков
    if len(lines) >= 10:
        # Проверка одновременных звонков
        calls_by_subscriber = {}
        for i, line in enumerate(lines[:10], 1):
            parts = [part.strip() for part in line.split(',')]
            if len(parts) != 5:
                continue
                
            call_type, subscriber, _, start_time, end_time = parts
            try:
                start_dt = datetime.fromisoformat(start_time)
                end_dt = datetime.fromisoformat(end_time)
            except ValueError:
                continue
            
            if subscriber not in calls_by_subscriber:
                calls_by_subscriber[subscriber] = []
            
            # Проверка пересечения временных интервалов
            for call in calls_by_subscriber[subscriber]:
                other_start, other_end, other_line = call
                if not (end_dt <= other_start or start_dt >= other_end):
                    call_dir = "исходящих" if call_type == '01' else "входящих"
                    errors["call_logic"].append(f"Конфликт {call_dir} вызовов")
                    print(
                        f"Строка {i}: Конфликт {call_dir} вызова с строкой {other_line} "
                        f"для абонента {subscriber} (пересечение временных интервалов)"
                    )
            
            calls_by_subscriber[subscriber].append((start_dt, end_dt, i))


    # Проверка хронологического порядка записей
    prev_start_time = None
    time_sequence_errors = []
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
            
        parts = [part.strip() for part in line.split(',')]
        if len(parts) != 5:
            continue
        
        _, _, _, start_time, _ = parts  # Нас интересует только время начала
        
        try:
            current_start = datetime.fromisoformat(start_time)
            
            if prev_start_time is not None and current_start < prev_start_time:
                time_sequence_errors.append(
                    f"Строка {i}: Нарушение хронологического порядка. "
                    f"Текущее время начала {start_time} раньше времени начала "
                    f"предыдущей записи {prev_start_time.isoformat()}"
                )
            
            # Обновляем время начала предыдущей записи
            # (только если текущая запись валидна)
            prev_start_time = current_start
                
        except ValueError:
            continue
    
    # Проверка звонков, пересекающих полночь
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
            
        parts = [part.strip() for part in line.split(',')]
        if len(parts) != 5:
            continue
        
        call_type, subscriber, contact, start_time, end_time = parts
        
        try:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
            
            # Проверка, что звонок пересекает полночь
            if start_dt.date() < end_dt.date():
                midnight = datetime.combine(end_dt.date(), time.min)
                
                # Проверяем, что это не разделенный звонок
                if not (start_dt == midnight or end_dt == midnight):
                    errors["midnight_crossing"].append("Звонок пересекает полночь и не делится на 2 звонка")
                    print(
                        f"Строка {i}: Звонок пересекает полночь (с {start_time} по {end_time}) "
                        f"и должен быть разделен на две записи: "
                        f"1) до 23:59:59 {start_dt.date()} и "
                        f"2) с 00:00:00 {end_dt.date()}"
                    )
                
        except ValueError:
            continue


    if time_sequence_errors:
        errors["time_sequence"] = time_sequence_errors
    
    # Удаляем пустые категории ошибок
    return {k: v for k, v in errors.items() if v}

def validate_all_cdr_files(directory: str) -> Dict[str, Dict[str, List[str]]]:
    """
    Валидирует все CDR файлы в указанной директории
    
    Args:
        directory (str): Путь к директории с CDR файлами
        
    Returns:
        Dict[str, Dict[str, List[str]]]: Результаты валидации для каждого файла
    """
    results = {}
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            results[filename] = validate_cdr_file(file_path)
    return results

# Пример использования
if __name__ == "__main__":
    validation_results = validate_all_cdr_files("C:/Users/anna/Desktop/CDR")
    
    for filename, errors in validation_results.items():
        print(f"\nРезультаты проверки файла {filename}:")
        if not errors:
            print("  Файл валиден, ошибок не обнаружено")
            continue
            
        for error_type, error_list in errors.items():
            print(f"  {error_type.upper()} ошибки:")
            for error in error_list:
                print(f"    - {error}")