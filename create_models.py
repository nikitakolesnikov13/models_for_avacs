from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, Numeric, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, foreign
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()


from sqlalchemy import Column, Integer, String, Boolean, Date, Numeric, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

class Software(Base):
    __tablename__ = 'software'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    version = Column(Integer, nullable=False)
    actual = Column(Boolean, nullable=False, default=False)
    devices = relationship("Devices", back_populates="software", cascade="all, delete-orphan")
    flights = relationship("Flights", back_populates="software")

class Devices(Base):
    __tablename__ = 'devices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Integer, nullable=False)
    name = Column(Integer, nullable=False)
    soft_id = Column(Integer, ForeignKey('software.id', ondelete='CASCADE'), nullable=False)
    serial = Column(Numeric(10, 2), nullable=False)
    software = relationship("Software", back_populates="devices")
    flights = relationship("Flights", back_populates="devices")

class Airplanes(Base):
    __tablename__ = 'airplanes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    number = Column(Integer, nullable=False)
    flights = relationship("Flights", back_populates="airplane")

class Context(Base):
    __tablename__ = 'context'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    bucket = Column(Integer, nullable=False)
    author_id = Column(Integer, nullable=False)
    flights_id = Column(Integer, ForeignKey('flights.id', ondelete='CASCADE'), nullable=False)
    flight = relationship("Flights", back_populates="context")

class Flights(Base):
    __tablename__ = 'flights'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    date = Column(Date, nullable=False)
    airplane_id = Column(Integer, ForeignKey('airplanes.id', ondelete='CASCADE'), nullable=False)
    incident_id = Column(Integer, ForeignKey('incident.id', ondelete='CASCADE'), nullable=True)
    devices_id = Column(Integer, ForeignKey('devices.id', ondelete='CASCADE'), nullable=False)
    software_id = Column(Integer, ForeignKey('software.id', ondelete='CASCADE'), nullable=False)
    radio_device = Column(Integer, ForeignKey('devices.id', ondelete='CASCADE'), nullable=True)
    autopilot_device = Column(Integer, ForeignKey('devices.id', ondelete='CASCADE'), nullable=True)
    servo_device = Column(Integer, ForeignKey('devices.id', ondelete='CASCADE'), nullable=True)
    airplane = relationship("Airplanes", back_populates="flights")
    incident = relationship("Incident", back_populates="flights")
    devices = relationship("Devices", foreign_keys=[devices_id], back_populates="flights")
    software = relationship("Software", back_populates="flights")
    context = relationship("Context", back_populates="flight")
    payloads = relationship("Payload", back_populates="flight", cascade="all, delete-orphan")

class Incident(Base):
    __tablename__ = 'incident'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String, nullable=False)
    flights = relationship("Flights", back_populates="incident", cascade="all, delete-orphan")

class Payload(Base):
    __tablename__ = 'payload'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    weight = Column(Integer, nullable=False)
    flight_id = Column(Integer, ForeignKey('flights.id', ondelete='CASCADE'), nullable=False)
    flight = relationship("Flights", back_populates="payloads")

# Создание таблиц в базе данных
def init_db(engine):
    Base.metadata.create_all(bind=engine)