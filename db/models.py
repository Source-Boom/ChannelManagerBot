#Классы, которые отображают способ хранения данных в БД

from sqlalchemy import Integer, String, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[str]                         = mapped_column(String, primary_key=True)
    balance: Mapped[int]                    = mapped_column(Integer)
    subscription_expiry: Mapped[datetime]   = mapped_column(DateTime)
    subscription: Mapped[bool]              = mapped_column(Boolean)


class SupportQuestion(Base):
    __tablename__                   = 'support_questions'
    user_message_id: Mapped[int]    = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str]            = mapped_column(String, nullable=False)
