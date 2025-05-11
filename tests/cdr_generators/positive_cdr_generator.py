from ast import Tuple
import os
from datetime import datetime, timedelta
import random
from typing import List, Optional

def generate_phone_number(operator_code: str = None) -> str:
    """Генерирует случайный номер телефона с возможностью указания кода оператора."""
    # Список возможных кодов операторов (можно расширить)
    operator_codes = ['900', '921', '999', '901', '902']
    
    # Если код оператора не указан, выбираем случайный
    if operator_code is None:
        operator_code = random.choice(operator_codes)
    
    # Формат: 7 (код страны) + код оператора (3 цифры) + остальные цифры (7 цифр)
    remaining_digits = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    return f"7{operator_code}{remaining_digits}"

def generate_timestamp(base_time: Optional[datetime] = None, 
                      min_duration: int = 1, 
                      max_duration: int = 300) -> Tuple[datetime, datetime]:
    """Генерирует временные метки начала и окончания звонка."""
    if base_time is None:
        base_time = datetime.now()
    
    # Генерируем случайное смещение от базового времени (до 1 часа)
    start_offset = random.randint(0, 3600)
    start_time = base_time + timedelta(seconds=start_offset)
    
    # Генерируем длительность звонка
    duration = random.randint(min_duration, max_duration)
    end_time = start_time + timedelta(seconds=duration)
    
    return start_time, end_time

def generate_split_call(base_time: datetime) -> List[Tuple[str, str, str, str, str]]:
    """Генерирует звонок, который пересекает полночь, разделяя его на две записи."""
    # Создаем звонок, который начинается до полуночи и заканчивается после
    call_type = random.choice(['01', '02'])
    subscriber = generate_phone_number()
    contact = generate_phone_number()
    
    # Устанавливаем время начала незадолго до полуночи
    start_time = datetime.combine(base_time.date(), datetime.max.time()) - timedelta(seconds=random.randint(5, 30))
    
    # Устанавливаем время окончания после полуночи
    end_time = datetime.combine(base_time.date() + timedelta(days=1), datetime.min.time()) + timedelta(seconds=random.randint(5, 60))
    
    # Разделяем звонок на две части
    first_part_end = datetime.combine(base_time.date(), datetime.max.time())
    second_part_start = datetime.combine(base_time.date() + timedelta(days=1), datetime.min.time())
    
    return [
        (call_type, subscriber, contact, start_time.isoformat(), first_part_end.isoformat()),
        (call_type, subscriber, contact, second_part_start.isoformat(), end_time.isoformat())
    ]

def generate_cdr_record(base_time: Optional[datetime] = None, 
                       allow_split_calls: bool = True) -> Tuple[str, str, str, str, str]:
    """Генерирует одну запись CDR."""
    call_type = random.choice(['01', '02'])
    
    # Первый номер всегда с кодом оператора '900'
    subscriber = generate_phone_number(operator_code='900')
    
    # Второй номер может быть с любым кодом оператора (включая '900')
    # 30% вероятность, что будет не '900'
    if random.random() < 0.3:
        contact = generate_phone_number()  # случайный код оператора
    else:
        contact = generate_phone_number(operator_code='900')
    
    # 10% chance to generate a call that crosses midnight
    if allow_split_calls and random.random() < 0.1 and base_time is not None:
        # Generate a call that crosses midnight
        start_time, end_time = generate_timestamp(
            base_time=datetime.combine(base_time.date(), datetime.max.time()) - timedelta(minutes=5),
            min_duration=60,
            max_duration=300
        )
    else:
        start_time, end_time = generate_timestamp(base_time)
    
    return (call_type, subscriber, contact, start_time.isoformat(), end_time.isoformat())

def generate_cdr_file(output_path: str, 
                     base_time: Optional[datetime] = None, 
                     num_records: int = 10) -> str:
    """
    Генерирует один CDR-файл с заданным количеством записей.
    
    Args:
        output_path (str): Путь для сохранения файла
        base_time (datetime, optional): Базовое время для генерации записей
        num_records (int): Количество записей в файле (по умолчанию 10)
        
    Returns:
        str: Путь к созданному файлу
    """
    if base_time is None:
        base_time = datetime.now()
    
    records = []
    records_remaining = num_records
    
    while records_remaining > 0:
        # 10% chance to generate a split call (which produces 2 records)
        if records_remaining >= 2 and random.random() < 0.1:
            split_records = generate_split_call(base_time)
            records.extend(split_records)
            records_remaining -= 2
        else:
            record = generate_cdr_record(base_time, allow_split_calls=False)
            records.append(record)
            records_remaining -= 1
    
    # Убедимся, что у нас ровно 10 записей
    records = records[:num_records]
    
    # Сортируем записи по времени начала
    records.sort(key=lambda x: x[3])
    
    # Формируем содержимое файла
    file_content = []
    for record in records:
        file_content.append(','.join(record))
    
    # Создаем директорию, если ее нет
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Сохраняем файл
    with open(output_path, 'w') as f:
        f.write('\n'.join(file_content))
    
    return output_path

def generate_multiple_cdr_files(output_dir: str, 
                              num_files: int, 
                              start_time: Optional[datetime] = None) -> List[str]:
    """
    Генерирует несколько CDR-файлов с общей временной логикой.
    
    Args:
        output_dir (str): Директория для сохранения файлов
        num_files (int): Количество файлов для генерации
        start_time (datetime, optional): Начальное время для первого файла
        
    Returns:
        List[str]: Список путей к созданным файлам
    """
    if start_time is None:
        start_time = datetime.now()
    
    generated_files = []
    current_time = start_time
    
    for i in range(num_files):
        filename = f"cdr_{current_time.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        file_path = os.path.join(output_dir, filename)
        
        generate_cdr_file(file_path, base_time=current_time)
        generated_files.append(file_path)
        
        # Сдвигаем время для следующего файла (например, на 15 минут)
        current_time += timedelta(minutes=15)
    
    return generated_files

# Пример использования
if __name__ == "__main__":
    # Создаем один файл
    single_file_path = generate_cdr_file("cdr_files/single_cdr.txt")
    print(f"Создан файл: {single_file_path}")
    
    # Создаем несколько файлов
    multiple_files = generate_multiple_cdr_files("cdr_files/multiple", 3)
    print("\nСозданы файлы:")
    for file_path in multiple_files:
        print(f"- {file_path}")