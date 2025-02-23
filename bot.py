import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from aiogram import Bot, Dispatcher
from handlers.start import router as start
from handlers.subscription import router as subscription
from handlers.support import router as support
from handlers.channel import router as channel

from services import subscription_checker

from db.crud import db

from config import TOKEN


bot = Bot(token=TOKEN)
dp = Dispatcher()

scheduler = AsyncIOScheduler()


async def on_startup():
    scheduler.add_job(
        subscription_checker.check_and_update_subscriptions,
        CronTrigger(hour=2, minute=0),
        kwargs={'bot': bot}
    )
    scheduler.add_job(
        subscription_checker.process_expired_subscriptions,
        CronTrigger(hour=2, minute=30),
        kwargs={'bot': bot}
    )
    scheduler.start()


async def on_shutdown():
    scheduler.shutdown()


from datetime import datetime


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.include_routers(start, subscription, support, channel)
    await dp.start_polling(bot)
    


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(db.close())