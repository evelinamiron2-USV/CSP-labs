import enum
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Text, Numeric, Boolean, DateTime, ForeignKey, UniqueConstraint, Enum
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Sex(str, enum.Enum):
    BOTH = "BTSX"
    MALE = "MLE"
    FEMALE = "FMLE"

class Source(Base):
    __tablename__ = "source"

    source_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    base_url = Column(String(255), nullable=True)

    indicators = relationship("Indicator", back_populates="source", cascade="all, delete-orphan")

class Country(Base):
    __tablename__ = "country"

    country_code = Column(String(3), primary_key=True)  # ISO3
    name = Column(String(100), nullable=False)
    region = Column(String(50), nullable=True)
    income_group = Column(String(50), nullable=True)

    observations = relationship("Observation", back_populates="country", cascade="all, delete-orphan")

class Indicator(Base):
    __tablename__ = "indicator"

    indicator_id = Column(Integer, primary_key=True)
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    unit = Column(String(50), nullable=True)
    source_id = Column(Integer, ForeignKey("source.source_id", ondelete="CASCADE"), nullable=True)

    source = relationship("Source", back_populates="indicators")
    observations = relationship("Observation", back_populates="indicator", cascade="all, delete-orphan")

class Observation(Base):
    __tablename__ = "observation"

    observation_id = Column(BigInteger, primary_key=True)
    country_code = Column(String(3), ForeignKey("country.country_code", ondelete="CASCADE"), nullable=False)
    indicator_id = Column(Integer, ForeignKey("indicator.indicator_id", ondelete="CASCADE"), nullable=False)
    year = Column(Integer, nullable=False)
    sex = Column(String(10), default="BTSX", nullable=False)
    value = Column(Numeric(15, 4), nullable=True)
    is_outlier = Column(Boolean, default=False, nullable=False)  # Cerința Task 2.2 pentru IQR Outliers
    rehab_coverage_index = Column(Numeric(5, 2), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    country = relationship("Country", back_populates="observations")
    indicator = relationship("Indicator", back_populates="observations")

    __table_args__ = (
        UniqueConstraint("country_code", "indicator_id", "year", "sex", name="uq_observation"),
    )

class ImportLog(Base):
    __tablename__ = "import_log"

    log_id = Column(Integer, primary_key=True)
    source_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)
    records_imported = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    executed_at = Column(DateTime, default=datetime.utcnow)