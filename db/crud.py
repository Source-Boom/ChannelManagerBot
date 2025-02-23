#Операции с БД: запись, получение данных и пр

import os
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from .models import Base, User, SupportQuestion

from typing import List

import asyncio

from .config import DB_PATH
from config import SUBSCRIPTION_PERIOD, SUBSCRIPTION_PRICE

class Database:
    def __init__(self):
        self.db_name = 'sqlite+aiosqlite:///' + str(DB_PATH)
        self.engine = create_async_engine(self.db_name, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)


    async def init_db(self):
        db_file = self.db_name.split(":///")[-1]
        if not os.path.exists(db_file):
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)


    async def get_user(self, user_id: str) -> User | None:
        async with self.SessionLocal() as session:
            stmt = select(User).where(User.id == user_id)
            result = await session.execute(stmt)
            return result.scalars().first()
        
    
    async def get_all_users(self) -> List[User]:
        async with self.SessionLocal() as session:
            stmt = select(User)
            result = await session.execute(stmt)
            return result.scalars().first()


    async def add_user(self, user_id: str, 
                       subscription_expiry: datetime = datetime.today().date(), 
                       balance: int = 0) -> bool:
        user = await self.get_user(user_id)
        if user:
            return False
        async with self.SessionLocal() as session, session.begin():
            new_user = User(id=user_id, balance=balance, subscription_expiry=subscription_expiry, subscription=False)
            session.add(new_user)
            return True


    async def replenish_user_balance(self, user_id: str, payment: int = SUBSCRIPTION_PRICE) -> bool:
        async with self.SessionLocal() as session, session.begin():
            stmt = select(User).where(User.id == user_id)
            result = await session.execute(stmt)
            user = result.scalars().first()
            if not user:
                return False
            user.balance += payment
            return True


    async def update_subscription(self, user_id: str) -> None:
        async with self.SessionLocal() as session:
            try:
                async with session.begin():
                    user = await session.get(User, user_id)
                    
                    if not user:
                        return False
                    
                    if user.balance < SUBSCRIPTION_PRICE:
                        return False
                    
                    user.subscription_expiry += timedelta(days=SUBSCRIPTION_PERIOD)
                    user.subscription = True
                    user.balance -= SUBSCRIPTION_PRICE                
            except:
                pass
    

    async def disable_subscription(self, user_id: str) -> None:
        async with self.SessionLocal() as session, session.begin():
            user = await self.get_user(user_id=user_id)
            if user:
                user.balance = False


    async def is_user(self, user_id: str) -> bool:
        user = await self.get_user(user_id)
        return user is not None


    async def is_user_subscription_active(self, user_id: str) -> bool:
        user = await self.get_user(user_id)
        if user:
            return user.subscription
        else:
            return False


    async def get_balance(self, user_id: str) -> int | None:
        user = await self.get_user(user_id)
        if user:
            return user.balance
        return None


    async def get_subscription_expiry(self, user_id: str) -> datetime | None:
        user = await self.get_user(user_id)
        if user:
            return user.subscription_expiry
        return None


    async def get_support_question(self, user_message_id: int) -> SupportQuestion | None:
        async with self.SessionLocal() as session:
            stmt = select(SupportQuestion).where(SupportQuestion.user_message_id == user_message_id)
            result = await session.execute(stmt)
            return result.scalars().first()


    async def store_user_support_message(self, user_message_id: int, user_id: str) -> bool:
        user_message = await self.get_support_question(user_message_id)
        if user_message:
            return False
        async with self.SessionLocal() as session, session.begin():
            new_message = SupportQuestion(user_message_id=user_message_id, user_id=user_id)
            session.add(new_message)
            return True


    async def get_user_id_by_support_message(self, user_message_id: int) -> str | None:
        user_message = await self.get_support_question(user_message_id)
        if user_message:
            return user_message.user_id
        return None


    async def close(self):
        await self.engine.dispose()


db = Database()

asyncio.run(db.init_db())
