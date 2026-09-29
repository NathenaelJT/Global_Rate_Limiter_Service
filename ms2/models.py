from database import Base
from sqlalchemy import Boolean, Column, Integer, String


# Table 1: Usage
class Usage(Base):
    __tablename__ = "usage"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, index=True)
    feature_name = Column(String)


# Table 2: Client_Status
class ClientStatus(Base):
    __tablename__ = "client_status"

    client_id = Column(String, primary_key=True, index=True)
    usage_limit_exceeded = Column(Boolean, default=False)
