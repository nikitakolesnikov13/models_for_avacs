from sqlalchemy import create_engine, Column, BigInteger, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Log(Base):
    __tablename__ = 'logs'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False)
    process_name = Column(String(100), nullable=False)
    subsystem = Column(String(100), nullable=False)
    log_level = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    
    def __repr__(self):
        return (f"<Log(id={self.id}, timestamp='{self.timestamp}', process='{self.process_name}', "
                f"subsystem='{self.subsystem}', level='{self.log_level}')>")

if __name__ == "__main__":
    engine = create_engine('postgresql://postgres:your_password@localhost:5432/logs', echo=True)
    Base.metadata.create_all(engine)