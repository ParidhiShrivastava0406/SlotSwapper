from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
from enum import Enum

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    password_hash = Column(String)
    events = relationship("Event", back_populates="user")

class EventStatus(str, Enum):
    BUSY = "BUSY"
    SWAPPABLE = "SWAPPABLE"
    SWAP_PENDING = "SWAP_PENDING"

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default=EventStatus.BUSY.value)
    user = relationship("User", back_populates="events")

class SwapStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class SwapRequest(Base):
    __tablename__ = "swap_requests"
    id = Column(Integer, primary_key=True, index=True)
    requester_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    responder_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    my_slot_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    their_slot_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    status = Column(String, nullable=False, default=SwapStatus.PENDING.value)
    created_at = Column(DateTime, default=datetime.utcnow)
