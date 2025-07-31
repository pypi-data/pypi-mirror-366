from datetime import datetime
from enum import Enum as PyEnum
from enum import IntEnum

from sqlalchemy import Column, DateTime, Float, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Units(PyEnum):
    m3 = "m3"
    kwh = "kwh"
    degc = "degc"


class Types(IntEnum):
    water = 1
    electricity = 2
    heat = 3
    temperature = 4


class TimeSign(Base):
    __abstract__ = True

    created_ts = Column(DateTime, default=datetime.utcnow)
    updated_ts = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class IdentityBase(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    tenant = Column(UUID(as_uuid=True))
    external_id = Column(Text, nullable=True)
    meter_id = Column(Text)


class MeasurementBase(IdentityBase, TimeSign, Base):
    __abstract__ = True

    measured_ts = Column(DateTime)
    value = Column(Float)


class UsageBase(IdentityBase, TimeSign, Base):
    __abstract__ = True

    start_ts = Column(DateTime)
    end_ts = Column(DateTime)
    consumption_ts = Column(DateTime)

    start_value = Column(Float)
    end_value = Column(Float)
    consumption = Column(Float)
