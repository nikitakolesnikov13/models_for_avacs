from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://belial:repent@localhost:5432/aircraft_db"

engine = create_engine(DATABASE_URL)

# Проверка подключения
with engine.connect() as connection:
    print("Подключение успешно!")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()