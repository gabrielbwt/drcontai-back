from sqlalchemy import Column, Integer, String, DateTime
from app.dal.database import Base

class PluggyConfig(Base):
    __tablename__ = "pluggy_config"

    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String)
    api_key_expiration = Column(DateTime)
    connect_token = Column(String)
    connect_token_expiration = Column(DateTime)