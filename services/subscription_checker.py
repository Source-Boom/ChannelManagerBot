from aiogram import Bot
from db.crud import db
from config import GROUP_ID, SUBSCRIPTION_PRICE

from datetime import datetime, timedelta



async def send_remainder(user_id: str, bot: Bot) -> None:
    try:
        user = await bot.get_chat(user_id)
        await bot.send_message(chat_id=user,
                               text='До конца подписки осталось 3 дня\n\nНе забудьте пополнить счет <3')
    except:
        pass


async def process_expired_subscriptions(bot: Bot) -> None:
    users = await db.get_all_users()
    for user in users:
        if not user.subscription_active:
            # Kick user
            await bot.ban_chat_member(chat_id=GROUP_ID, user_id=user.id)
            await bot.unban_chat_member(chat_id=GROUP_ID, user_id=user.id)


async def check_and_update_subscriptions(bot: Bot) -> None:
    users = await db.get_all_users()
    for user in users:
        if user.subscription_expiry == datetime.today().date() and user.balance >= SUBSCRIPTION_PRICE:
            await db.update_subscription(user_id=user.id)
        elif user.subsription_expiry == (datetime.today().date() - timedelta(days=3)):
            await send_remainder(user_id=user.id)
        elif user.subsription_expiry == (datetime.today().date() + timedelta(days=1)):
            await db.disablpe_subscription(user_id=user.id)