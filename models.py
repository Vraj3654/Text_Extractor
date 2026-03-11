from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base
import datetime

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    raw_text = Column(Text, nullable=True)
    corrected_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
