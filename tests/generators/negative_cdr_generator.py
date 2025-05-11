import os
from datetime import datetime, timedelta
import random
from typing import Dict, List, Optional, Tuple

from tests.cdr_generators.positive_cdr_generator import generate_phone_number

def generate_error_cdr_file(output_path: str, 
                          error_config: Dict[str, int],
                          base_time: Optional[datetime] = None,
                          num_records: int = 10) -> str:
    """
    Генерирует CDR-файл с заданными ошибками.
    
    Args:
        output_path (str): Путь для сохранения файла
        error_config (Dict[str, int]): Конфигурация ошибок (тип: количество)
        base_time (datetime, optional): Базовое время для генерации записей
        num_records (int): Количество записей в файле
        
    Returns:
        str: Путь к созданному файлу
    """
    if base_time is None:
        base_time = datetime.now()
    
    # Генерируем сначала валидные записи
    records = []
    for _ in range(num_records):
        call_type = random.choice(['01', '02'])
        subscriber = f"79{random.randint(0, 9)}{''.join(random.choices('0123456789', k=7))}"
        contact = f"79{random.randint(0, 9)}{''.join(random.choices('0123456789', k=7))}"
        start_time, end_time = generate_timestamp(base_time)
        records.append((call_type, subscriber, contact, start_time.isoformat(), end_time.isoformat()))
    
    # Вносим ошибки согласно конфигу
    for error_type, count in error_config.items():
        for _ in range(count):
            if error_type == "file_structure":
                # Слишком много или мало записей
                if random.choice([True, False]):
                    records = records[:random.randint(1, 5)]  # слишком мало
                else:
                    records.extend([generate_valid_record(base_time) for _ in range(random.randint(11, 15))])  # слишком много
            
            elif error_type == "record_format":
                # Неправильное количество полей или тип вызова
                idx = random.randint(0, len(records)-1)
                if random.choice([True, False]):
                    # Неправильный тип вызова
                    records[idx] = (random.choice(['03', 'AB', '']), *records[idx][1:])
                else:
                    # Неправильное количество полей
                    records[idx] = records[idx][:random.choice([2, 3, 4])]
            
            elif error_type == "phone_numbers":
                # Неправильные номера телефонов
                idx = random.randint(0, len(records)-1)
                field = random.choice(['subscriber', 'contact'])
                if field == 'subscriber':
                    # Первый номер с ошибкой
                    records[idx] = (
                        records[idx][0],
                        generate_invalid_phone(),
                        records[idx][2],
                        *records[idx][3:]
                    )
                else:
                    # Второй номер с ошибкой
                    records[idx] = (
                        records[idx][0],
                        records[idx][1],
                        generate_invalid_phone(),
                        *records[idx][3:]
                    )
            
            elif error_type == "timestamps":
                # Неправильные временные метки
                idx = random.randint(0, len(records)-1)
                if random.choice([True, False]):
                    # Время окончания раньше времени начала
                    start = datetime.fromisoformat(records[idx][3])
                    end = start - timedelta(seconds=random.randint(1, 60))
                    records[idx] = (
                        *records[idx][:3],
                        start.isoformat(),
                        end.isoformat()
                    )
                else:
                    # Некорректный формат времени
                    records[idx] = (
                        *records[idx][:3],
                        "2025-13-01T25:61:61",  # явно неверная дата
                        records[idx][4]
                    )
            
            elif error_type == "call_logic":
                # Конфликтующие звонки
                idx = random.randint(0, len(records)-1)
                sub = records[idx][1]
                start = datetime.fromisoformat(records[idx][3])
                end = datetime.fromisoformat(records[idx][4])
                
                # Создаем конфликтующий звонок
                conflict_record = (
                    random.choice(['01', '02']),
                    sub,
                    generate_phone_number(),
                    (start + timedelta(seconds=1)).isoformat(),
                    (end - timedelta(seconds=1)).isoformat()
                )
                records.insert(random.randint(0, len(records)), conflict_record)
            
            elif error_type == "security":
                # Возможные SQL-инъекции
                idx = random.randint(0, len(records)-1)
                field = random.choice([0, 1, 2, 3, 4])
                sql_injection = random.choice([
                    "'; DROP TABLE calls; --",
                    "' OR '1'='1",
                    "1; SELECT * FROM users"
                ])
                records[idx] = tuple(
                    sql_injection if i == field else val 
                    for i, val in enumerate(records[idx])
                )
            
            elif error_type == "time_sequence":
                # Нарушение хронологического порядка
                if len(records) > 1:
                    idx = random.randint(1, len(records)-1)
                    records[idx], records[idx-1] = records[idx-1], records[idx]
            
            elif error_type == "midnight_crossing":
                # Звонок через полночь без разделения
                idx = random.randint(0, len(records)-1)
                start = datetime.combine(base_time.date(), datetime.max.time()) - timedelta(minutes=5)
                end = datetime.combine(base_time.date() + timedelta(days=1), datetime.min.time()) + timedelta(minutes=1)
                records[idx] = (
                    records[idx][0],
                    records[idx][1],
                    records[idx][2],
                    start.isoformat(),
                    end.isoformat()
                )
            
            elif error_type == "operator_code":
                # Неправильный код оператора
                idx = random.randint(0, len(records)-1)
                field = random.choice([1, 2])  # 1 - subscriber, 2 - contact
                if field == 1:
                    # Для subscriber всегда должен быть 900, но мы делаем ошибку
                    records[idx] = (
                        records[idx][0],
                        f"7{random.choice(['921', '999', '123'])}{''.join(random.choices('0123456789', k=7))}",
                        records[idx][2],
                        *records[idx][3:]
                    )
                else:
                    # Для contact делаем невалидный код оператора
                    records[idx] = (
                        records[idx][0],
                        records[idx][1],
                        f"7{random.choice(['000', '999', 'ABC'])}{''.join(random.choices('0123456789', k=7))}",
                        *records[idx][3:]
                    )
    
    # Сортируем записи по времени (если не было ошибки time_sequence)
    if "time_sequence" not in error_config or error_config["time_sequence"] == 0:
        records.sort(key=lambda x: x[3])
    
    # Сохраняем файл
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write('\n'.join([','.join(map(str, record)) for record in records]))
    
    return output_path

# Вспомогательные функции
def generate_valid_record(base_time: datetime) -> Tuple[str, str, str, str, str]:
    """Генерирует одну валидную запись CDR."""
    call_type = random.choice(['01', '02'])
    subscriber = f"7900{''.join(random.choices('0123456789', k=7))}"
    contact = f"79{random.choice(['00', '21', '99'])}{''.join(random.choices('0123456789', k=7))}"
    start_time, end_time = generate_timestamp(base_time)
    return (call_type, subscriber, contact, start_time.isoformat(), end_time.isoformat())

def generate_invalid_phone() -> str:
    """Генерирует невалидный номер телефона."""
    errors = [
        ''.join(random.choices('0123456789', k=random.randint(8, 12))),  # неправильная длина
        '7' + ''.join(random.choices('0123456789ABCDEF', k=10)),  # содержит буквы
        '',  # пустой номер
        '123'  # слишком короткий
    ]
    return random.choice(errors)

def generate_timestamp(base_time: datetime) -> Tuple[datetime, datetime]:
    """Генерирует валидные временные метки."""
    start_offset = random.randint(0, 3600)
    start_time = base_time + timedelta(seconds=start_offset)
    duration = random.randint(1, 300)
    end_time = start_time + timedelta(seconds=duration)
    return start_time, end_time

# Пример использования
if __name__ == "__main__":
    # Конфигурация ошибок
    error_config = {
        "phone_numbers": 2,  # 2 ошибки в номерах телефонов
        "timestamps": 1,     # 1 ошибка во временных метках
        "operator_code": 1   # 1 ошибка в коде оператора
    }
    
    # Генерация файла с ошибками
    output_path = generate_error_cdr_file(
        "error_cdr.txt",
        error_config=error_config,
        num_records=10
    )
    
    print(f"Сгенерирован файл с ошибками: {output_path}")