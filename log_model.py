from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Создаем базовый класс для моделей
Base = declarative_base()

# Модель логов
class Log(Base):
    __tablename__ = 'logs'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    process_name = Column(String(50), nullable=False)
    log_level = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    
    def __repr__(self):
        return f"<Log(timestamp='{self.timestamp}', process='{self.process_name}', level='{self.log_level}')>"

# Пример создания базы данных
if __name__ == "__main__":
    # Создаем подключение к базе данных SQLite
    engine = create_engine('sqlite:///logs.db', echo=True)
    
    # Создаем таблицы
    Base.metadata.create_all(engine)