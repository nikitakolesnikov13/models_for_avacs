from sqlalchemy import Column, Integer, String, DateTime, Enum, Float, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import enum
import pandas as pd
import re

Base = declarative_base()


class LogLevel(enum.Enum):
    INFO = "INFO"
    ERROR = "ERROR"
    DEBUG = "DEBUG"


class MessageType(enum.Enum):
    TELEMETRY = "telemetry"
    COMMAND = "command"
    REPORT = "report"
    CHANNEL = "channel"
    RECEIVER = "receiver"
    CONNECTION = "connection"


class UAVLogEntry(Base):
    __tablename__ = "uav_log_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    level = Column(Enum(LogLevel), nullable=False)
    message_type = Column(Enum(MessageType), nullable=False)
    callsign = Column(String, nullable=False)
    uid = Column(String, nullable=True)
    code = Column(Integer, nullable=True)
    ceid = Column(String, nullable=True)
    report_id = Column(Integer, nullable=True)
    ln = Column(Integer, nullable=True)
    content = Column(String, nullable=True)
    errno = Column(Integer, nullable=True)
    channel = Column(String, nullable=True)
    attempts = Column(Integer, nullable=True)

    def __repr__(self):
        return (f"<UAVLogEntry(timestamp={self.timestamp}, level={self.level}, "
                f"message_type={self.message_type}, callsign={self.callsign})>")


# Новая модель для хранения телеметрических данных
class UAVTelemetryData(Base):
    __tablename__ = "uav_telemetry_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    time_offset = Column(Float, nullable=False)  # Время из файла (например, 1.219999)
    callsign = Column(String, nullable=False, default="UNKNOWN")

    # Основные параметры полета
    roll = Column(Float, nullable=True)
    pitch = Column(Float, nullable=True)
    yaw = Column(Float, nullable=True)

    # Угловые скорости
    ang_rate_x = Column(Float, nullable=True)
    ang_rate_y = Column(Float, nullable=True)
    ang_rate_z = Column(Float, nullable=True)

    # Ускорения
    a_n = Column(Float, nullable=True)  # north
    a_e = Column(Float, nullable=True)  # east
    a_u = Column(Float, nullable=True)  # up

    # Скорости GNSS
    vel_gnss_n = Column(Float, nullable=True)
    vel_gnss_e = Column(Float, nullable=True)
    vel_gnss_u = Column(Float, nullable=True)

    # Позиции
    pos_ins_n = Column(Float, nullable=True)
    pos_ins_e = Column(Float, nullable=True)
    pos_ins_u = Column(Float, nullable=True)

    # GNSS координаты
    gnss_lat = Column(Float, nullable=True)
    gnss_lon = Column(Float, nullable=True)
    gnss_alt = Column(Float, nullable=True)

    # Барометрические данные
    bar_alt = Column(Float, nullable=True)
    bar_alt_rate = Column(Float, nullable=True)

    # Данные батареи
    bat_voltage = Column(Float, nullable=True)
    bat_current = Column(Float, nullable=True)
    bat_temp = Column(Float, nullable=True)
    bat_percentage = Column(Float, nullable=True)

    # Обороты роторов
    rotor_front_left_rpm = Column(Float, nullable=True)
    rotor_front_right_rpm = Column(Float, nullable=True)
    rotor_rear_right_rpm = Column(Float, nullable=True)
    rotor_rear_left_rpm = Column(Float, nullable=True)

    # Сохраняем все остальные данные как JSON-строку
    raw_data = Column(String, nullable=True)

    def __repr__(self):
        return (f"<UAVTelemetryData(time_offset={self.time_offset}, "
                f"lat={self.gnss_lat}, lon={self.gnss_lon}, alt={self.gnss_alt})>")


class UAVDataParser:
    def __init__(self, database_url="sqlite:///uav_data.db"):
        """
        Инициализация парсера данных БПЛА

        Args:
            database_url: URL базы данных (по умолчанию SQLite)
        """
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def parse_telemetry_file(self, file_path, callsign="UAV001"):
        """
        Парсит файл телеметрии и сохраняет данные в БД

        Args:
            file_path: путь к файлу с данными
            callsign: позывной БПЛА
        """
        try:
            # Читаем файл
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            lines = content.strip().split('\n')
            if len(lines) < 2:
                raise ValueError("Файл должен содержать минимум 2 строки (заголовки и данные)")

            # Парсим заголовки
            header_line = lines[0]
            headers = self._parse_headers(header_line)

            print(f"Найдено {len(headers)} колонок")
            print(f"Первые 10 колонок: {headers[:10]}")

            # Парсим данные
            data_lines = lines[1:]
            parsed_count = 0

            for line_num, line in enumerate(data_lines, 1):
                try:
                    values = self._parse_data_line(line)
                    print(f"Строка {line_num}: найдено {len(values)} значений")

                    # Если значений меньше чем заголовков, дополняем None
                    while len(values) < len(headers):
                        values.append(None)

                    # Если значений больше чем заголовков, обрезаем
                    if len(values) > len(headers):
                        values = values[:len(headers)]

                    # Создаем словарь данных
                    data_dict = dict(zip(headers, values))

                    # Создаем запись телеметрии
                    telemetry_entry = self._create_telemetry_entry(data_dict, callsign)
                    self.session.add(telemetry_entry)

                    # Создаем запись лога
                    log_entry = self._create_log_entry(data_dict, callsign, line_num)
                    self.session.add(log_entry)

                    parsed_count += 1

                    if parsed_count % 100 == 0:
                        print(f"Обработано {parsed_count} записей...")
                        self.session.commit()

                except Exception as e:
                    print(f"Ошибка в строке {line_num}: {e}")
                    continue

            # Сохраняем оставшиеся данные
            self.session.commit()
            print(f"Успешно обработано {parsed_count} записей")

            return parsed_count

        except Exception as e:
            print(f"Ошибка при обработке файла: {e}")
            self.session.rollback()
            return 0

    def _parse_headers(self, header_line):
        """Парсит строку заголовков"""
        # Пробуем разные разделители
        possible_separators = ['\t', '  ', ' ', ',', ';']
        headers = None

        for sep in possible_separators:
            test_headers = header_line.split(sep)
            if len(test_headers) > 100:  # Если много колонок, вероятно правильный разделитель
                headers = test_headers
                print(f"Используется разделитель: '{sep}' (найдено {len(headers)} колонок)")
                break

        if headers is None:
            # Если не нашли подходящий разделитель, используем пробелы
            headers = header_line.split()
            print(f"Используется разделитель пробелы (найдено {len(headers)} колонок)")

        # Очищаем заголовки от лишних символов и пробелов
        cleaned_headers = []
        for header in headers:
            if header.strip():  # Пропускаем пустые заголовки
                # Убираем единицы измерения в скобках и лишние символы
                clean_header = re.sub(r'\s*\([^)]*\)\s*', '', header.strip())
                clean_header = clean_header.replace(' ', '_').replace(',', '').replace('-', '_')
                cleaned_headers.append(clean_header)

        return cleaned_headers

    def _parse_data_line(self, line):
        """Парсит строку данных"""
        # Пробуем те же разделители что и для заголовков
        possible_separators = ['\t', '  ', ' ', ',', ';']
        values = None

        for sep in possible_separators:
            test_values = line.split(sep)
            # Фильтруем пустые значения если разделитель - пробел
            if sep == ' ':
                test_values = [v for v in test_values if v.strip()]

            if len(test_values) > 50:  # Если много значений, вероятно правильный разделитель
                values = test_values
                break

        if values is None:
            # Используем пробелы как последний вариант
            values = line.split()

        parsed_values = []

        for value in values:
            value = value.strip()
            if value == '' or value == '-':
                parsed_values.append(None)
            else:
                try:
                    # Пробуем преобразовать в число
                    if '.' in value:
                        parsed_values.append(float(value))
                    else:
                        parsed_values.append(int(value))
                except ValueError:
                    # Если не число, оставляем как строку
                    parsed_values.append(value)

        return parsed_values

    def _create_telemetry_entry(self, data_dict, callsign):
        """Создает запись телеметрии из словаря данных"""
        # Извлекаем время из первого столбца (например, "Time, t0=10-34-23.079")
        time_key = list(data_dict.keys())[0]
        time_offset = data_dict[time_key] if time_key in data_dict else 0.0

        # Маппинг ключей данных на поля модели
        field_mapping = {
            'roll': 'roll',
            'pitch': 'pitch',
            'yaw': 'yaw',
            'ang_rate_x': 'ang_rate_x',
            'ang_rate_y': 'ang_rate_y',
            'ang_rate_z': 'ang_rate_z',
            'a_n': 'a_n',
            'a_e': 'a_e',
            'a_u': 'a_u',
            'vel_gnss_n': 'vel_gnss_n',
            'vel_gnss_e': 'vel_gnss_e',
            'vel_gnss_u': 'vel_gnss_u',
            'pos_ins_n': 'pos_ins_n',
            'pos_ins_e': 'pos_ins_e',
            'pos_ins_u': 'pos_ins_u',
            'gnss_lat': 'gnss_lat',
            'gnss_lon': 'gnss_lon',
            'gnss_alt': 'gnss_alt',
            'bar_alt': 'bar_alt',
            'bar_alt_rate': 'bar_alt_rate',
            'bat_voltage': 'bat_voltage',
            'bat_current': 'bat_current',
            'bat_temp': 'bat_temp',
            'bat_percentage': 'bat_percentage',
            'rotor_front_left_rpm': 'rotor_front_left_rpm',
            'rotor_front_right_rpm': 'rotor_front_right_rpm',
            'rotor_rear_right_rpm': 'rotor_rear_right_rpm',
            'rotor_rear_left_rpm': 'rotor_rear_left_rpm'
        }

        # Создаем объект телеметрии
        telemetry_data = {
            'time_offset': time_offset,
            'callsign': callsign,
            'raw_data': str(data_dict)[:1000]  # Ограничиваем размер
        }

        # Заполняем поля из маппинга
        for data_key, field_name in field_mapping.items():
            if data_key in data_dict:
                telemetry_data[field_name] = data_dict[data_key]

        return UAVTelemetryData(**telemetry_data)

    def _create_log_entry(self, data_dict, callsign, line_num):
        """Создает запись лога"""
        return UAVLogEntry(
            level=LogLevel.INFO,
            message_type=MessageType.TELEMETRY,
            callsign=callsign,
            content=f"Телеметрия строка {line_num}: lat={data_dict.get('gnss_lat', 'N/A')}, "
                    f"lon={data_dict.get('gnss_lon', 'N/A')}, alt={data_dict.get('gnss_alt', 'N/A')}"
        )

    def get_telemetry_data(self, callsign=None, limit=None):
        """Получает данные телеметрии из БД"""
        query = self.session.query(UAVTelemetryData)

        if callsign:
            query = query.filter(UAVTelemetryData.callsign == callsign)

        if limit:
            query = query.limit(limit)

        return query.all()

    def close(self):
        """Закрывает соединение с БД"""
        self.session.close()


# Пример использования
if __name__ == "__main__":
    # Создаем парсер
    parser = UAVDataParser()

    # Парсим файл (замените на путь к вашему файлу)
    file_path = "boss.txt"
    callsign = "UAV_TEST_001"

    print("Начинаем парсинг файла...")
    count = parser.parse_telemetry_file(file_path, callsign)
    print(f"Обработано записей: {count}")

    # Получаем некоторые данные для проверки
    print("\nПримеры данных из БД:")
    data = parser.get_telemetry_data(callsign=callsign, limit=5)
    for entry in data:
        print(f"Время: {entry.time_offset}, Координаты: ({entry.gnss_lat}, {entry.gnss_lon}), "
              f"Высота: {entry.gnss_alt}, Крен: {entry.roll}")

    # Закрываем парсер
    parser.close()
    print("\nГотово!")