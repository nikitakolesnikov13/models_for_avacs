from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DatabaseConnector:
    """Условный коннектор для управления подключением к базе данных PostgreSQL."""
    
    def __init__(self, connection_string='postgresql://myuser:mypassword@localhost:5432/logs'):
        self.connection_string = connection_string
        self.engine = None
        self.Session = None

    def connect(self):
        if self.engine is None:
            self.engine = create_engine(self.connection_string, echo=True)
            self.Session = sessionmaker(bind=self.engine)
        return self.engine

    def get_session(self):
        if self.Session is None:
            self.connect()
        return self.Session()

    def disconnect(self):
        if self.engine is not None:
            self.engine.dispose()
            self.engine = None
            self.Session = None

    def clear_table(self, table_name):
        if self.engine is None:
            self.connect()
        with self.engine.connect() as conn:
            conn.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY")
            conn.commit()
            print(f"Table {table_name} cleared")