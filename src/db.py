import os
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, ARRAY, DateTime
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class Program(Base):
    __tablename__ = "programs"

    id                = Column(Integer, primary_key=True, index=True)
    intent            = Column(String, index=True, nullable=False)
    code              = Column(Text, nullable=False)
    compile_attempts  = Column(Integer, nullable=False)
    logic_failures    = Column(Integer, nullable=False)
    tags              = Column(ARRAY(String), nullable=False)
    created_at        = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
