from datetime import datetime
import re
import os
from sqlalchemy import inspect
from db_connector import DatabaseConnector
from log_model import Log, Base

# Функция для извлечения даты из сообщения
def extract_date_from_message(message):
    """Извлекает дату в формате 'MMM DD YYYY' (например, 'Jan 16 2025') из сообщения."""
    date_pattern = r'([A-Za-z]{3} \d{1,2} \d{4})'
    match = re.search(date_pattern, message)
    if match:
        date_str = match.group(1)
        try:
            return datetime.strptime(date_str, "%b %d %Y")
        except ValueError:
            return None
    return None

# Функция для парсинга строки лога
def parse_log_line(line):
    """Парсит строку лога, разделенную пробелами, и возвращает словарь с данными."""
    pattern = r'(\d{2}-\d{2}-\d{2}\.\d{3})\s+([\w-]+)\s+(\w+)\s+(\w+)\s+(.+)'
    match = re.match(pattern, line.strip())
    if match:
        timestamp_str, process_name, subsystem, log_level, message = match.groups()
        try:
            time_part = timestamp_str.replace('-', ':')
            date_from_message = extract_date_from_message(message)
            if date_from_message:
                timestamp = datetime.strptime(f"{date_from_message.date()} {time_part}", "%Y-%m-%d %H:%M:%S.%f")
            else:
                timestamp = datetime.strptime(f"{datetime.now().date()} {time_part}", "%Y-%m-%d %H:%M:%S.%f")
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
def insert_logs_from_files(directory, db_connector, batch_size=1000):
    """Обрабатывает лог-файлы в директории и вставляет данные в базу PostgreSQL."""
    session = db_connector.get_session()
    total_inserted = 0
    try:
        # Проверяем, существует ли таблица
        inspector = inspect(db_connector.connect())
        if inspector.has_table('logs'):
            print("Table 'logs' exists and is ready for insertion.")
        else:
            print("Table 'logs' does not exist! Creating it now...")
            Base.metadata.create_all(db_connector.connect())
        
        print(f"Scanning directory: {directory}")
        files = [f for f in os.listdir(directory) if f.endswith('.txt')]
        print(f"Files found: {files}")
        
        for filename in files:
            file_path = os.path.join(directory, filename)
            log_entries = []
            
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                print(f"File {filename} contains {len(lines)} lines")
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
    # Настройка коннектора к PostgreSQL
    connection_string = 'postgresql://postgres:your_password@localhost:5432/logs'  # Укажите вашу строку подключения
    db_connector = DatabaseConnector(connection_string)
    
    # Подключаемся и создаем таблицы
    engine = db_connector.connect()
    Base.metadata.create_all(engine)
    
    # Путь к директории с лог-файлами
    log_directory = "/home/lazarus/sys"  # Укажите правильный путь
    insert_logs_from_files(log_directory, db_connector)
    
    # Отключаемся от базы данных
    db_connector.disconnect()