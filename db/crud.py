#Операции с БД: запись, получение данных и пр

import os
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import create_engine, update, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from .models import Base, User, SupportQuestion, Payment, TopicIDs

from typing import List

import asyncio

from .config import DB_PATH
from config import SUBSCRIPTION_PERIOD, SUBSCRIPTION_PRICE

class Database:
    def __init__(self):
        self.db_name = 'sqlite+aiosqlite:///' + str(DB_PATH)
        self.engine = create_async_engine(self.db_name, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)
        # Синхронный движок и сессия
        self.sync_db_name = 'sqlite:///' + str(DB_PATH)
        self.sync_engine = create_engine(self.sync_db_name, echo=False)
        self.SyncSessionLocal = sessionmaker(bind=self.sync_engine, expire_on_commit=False)


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
            return result.scalars()


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
            user = await session.get(User, user_id)
            if user.subscription:
                user.subscription = False


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


    async def create_topic_for_user(self, user_id: int, topic_id: int) -> None:
        async with self.SessionLocal() as session, session.begin():
            new_topic = TopicIDs(topic_id=topic_id, user_id=user_id)
            session.add(new_topic)


    async def get_topic_by_user_id(self, user_id: int) -> int | None:
        async with self.SessionLocal() as session:
            stmt = select(TopicIDs).where(TopicIDs.user_id == user_id)
            result = await session.execute(stmt)
            need_res = result.scalars().first()
            if need_res != None:
                return need_res.topic_id
            else:
                return None
            
    async def get_user_id_by_topic(self, topic_id: int) -> int | None:
        async with self.SessionLocal() as session:
            stmt = select(TopicIDs).where(TopicIDs.topic_id == topic_id)
            result = await session.execute(stmt)
            need_res = result.scalars().first()
            if need_res != None:
                return need_res.user_id
            else:
                return None


    async def get_user_id_by_support_message(self, user_message_id: int) -> str | None:
        user_message = await self.get_support_question(user_message_id)
        if user_message:
            return user_message.user_id
        return None

    async def create_new_payment(self, user_id: int, message_id: int):
        async with self.SessionLocal() as session, session.begin():
            new_payment = Payment(user_id=user_id, status=0, message_id=message_id)
            session.add(new_payment)
        async with self.SessionLocal() as session:
            stmt = select(Payment).where(Payment.message_id == message_id)
            result = await session.execute(stmt)
            return result.scalars().first().payment_id

    def select_payment(self, pay_id: int):
        with self.SyncSessionLocal() as session:
            stmt = select(Payment).where(and_(Payment.payment_id == pay_id, Payment.status == 0))
            result = session.execute(stmt)
            payment = result.scalars().first()
            
            if payment:
                update_stmt = update(Payment).where(Payment.payment_id == pay_id).values(status=1)
                session.execute(update_stmt)
                session.commit()  # Сохраняем изменения в базе данных
                
                return payment.user_id
            else:
                return None

    def get_user_sync(self, user_id: str) -> User | None:
        with self.SyncSessionLocal()  as session:
            stmt = select(User).where(User.id == user_id)
            result = session.execute(stmt)
            return result.scalars().first()

    def is_user_sync(self, user_id: str) -> bool:
        user = self.get_user_sync(user_id)
        return user is not None
    
    def add_user_sync(self, user_id: str, 
                       subscription_expiry: datetime = datetime.today().date(), 
                       balance: int = 0) -> bool:
        user = self.get_user_sync(user_id)
        if user:
            return False
        with self.SyncSessionLocal()  as session, session.begin():
            new_user = User(id=user_id, balance=balance, subscription_expiry=subscription_expiry, subscription=False)
            session.add(new_user)
            return True

    def replenish_user_balance_sync(self, user_id: str, payment: int = SUBSCRIPTION_PRICE) -> bool:
        with self.SyncSessionLocal()  as session, session.begin():
            stmt = select(User).where(User.id == user_id)
            result = session.execute(stmt)
            user = result.scalars().first()
            if not user:
                return False
            user.balance += payment
            return True
        
    def is_user_subscription_active_sync(self, user_id: str) -> bool:
        user = self.get_user_sync(user_id)
        if user:
            return user.subscription
        else:
            return False
        
    def update_subscription_sync(self, user_id: str) -> None:
        with self.SyncSessionLocal()  as session:
            try:
                with session.begin():
                    user = session.get(User, user_id)
                    
                    if not user:
                        return False
                    
                    if user.balance < SUBSCRIPTION_PRICE:
                        return False
                    
                    user.subscription_expiry += timedelta(days=SUBSCRIPTION_PERIOD)
                    user.subscription = True
                    user.balance -= SUBSCRIPTION_PRICE                
            except:
                pass


    async def close(self):
        await self.engine.dispose()


db = Database()

asyncio.run(db.init_db())
