from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import re
import os

# Импортируем модель Log
from log_model import Log, Base

# Функция для парсинга строки лога
def parse_log_line(line):
    """Парсит строку лога, разделенную пробелами, и возвращает словарь с данными."""
    # Регулярное выражение для строк вида: "06-40-58.142    fadapt-mavlink  System  INFO    execute shell..."
    pattern = r'(\d{2}-\d{2}-\d{2}\.\d{3})\s+([\w-]+)\s+(\w+)\s+(\w+)\s+(.+)'
    match = re.match(pattern, line.strip())
    if match:
        timestamp_str, process_name, subsystem, log_level, message = match.groups()
        try:
            # Извлекаем дату из сообщения, если она есть
            date_pattern = r'([A-Za-z]{3} \d{1,2} \d{4})'
            date_match = re.search(date_pattern, message)
            if date_match:
                date_str = date_match.group(1)
                # Комбинируем дату из сообщения и время из строки
                timestamp = datetime.strptime(f"{date_str} {timestamp_str.replace('-', ':')}", "%b %d %Y %H:%M:%S.%f")
            else:
                # Если даты нет, используем текущую дату
                timestamp = datetime.strptime(f"{datetime.now().date()} {timestamp_str.replace('-', ':')}", "%Y-%m-%d %H:%M:%S.%f")
            
            return {
                'timestamp': timestamp,
                'process_name': process_name,
                'subsystem': subsystem,
                'log_level': log_level,
                'message': message
            }
        except ValueError as e:
            print(f"Timestamp parse error for line: {line.strip()} - {e}")
            return None
    else:
        print(f"Line does not match pattern: {line.strip()}")
        return None

# Функция для обработки файлов и вставки данных
def insert_logs_from_files(directory, engine, batch_size=1000):
    """Обрабатывает лог-файлы в директории и вставляет данные в базу."""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    total_inserted = 0
    try:
        print(f"Scanning directory: {directory}")
        files = [f for f in os.listdir(directory) if f.endswith('.txt')]
        print(f"Files found: {files}")
        
        for filename in files:
            file_path = os.path.join(directory, filename)
            log_entries = []
            
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                print ("diede(filename) contains {len(lines)} lines")
                for line in lines:
                    parsed_log = parse_log_line(line)
                    if parsed_log:
                        log_entries.append(parsed_log)
                    
                    if len(log_entries) >= batch_size:
                        session.bulk_insert_mappings(Log, log_entries)
                        total_inserted += len(log_entries)
                        print(f"Inserted {len(log_entries)} logs from {filename} (total: {total_inserted})")
                        log_entries = []
            
            if log_entries:
                session.bulk_insert_mappings(Log, log_entries)
                total_inserted += len(log_entries)
                print(f"Inserted {len(log_entries)} logs from {filename} (total: {total_inserted})")
        
        session.commit()
        print(f"Total logs inserted: {total_inserted}")
    except Exception as e:
        print(f"Error occurred: {e}")
        session.rollback()
    finally:
        session.close()

# Основной блок
if __name__ == "__main__":
    engine = create_engine('sqlite:///logs.db', echo=True)
    Base.metadata.create_all(engine)
    
    log_directory = "/home/lazarus/sys"  # Укажите правильный путь
    insert_logs_from_files(log_directory, engine)