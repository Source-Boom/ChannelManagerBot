from aiogram import Bot
from db.crud import db
from config import GROUP_ID, SUBSCRIPTION_PRICE, SUBSCRIPTION_PERIOD

from datetime import datetime, timedelta, date



async def send_remainder(user_id: str, bot: Bot) -> None:
    try:
        #user = await bot.get_chat(user_id)
        await bot.send_message(chat_id=user_id,
                               text='Через 3 дня ваша подписка на канал Style by Inna закончится. Чтобы не потерять доступ к нему, пополните счёт с помощью кнопки Подписка 👇🏻')
    except Exception as e:
        print(e)


#async def process_expired_subscriptions(bot: Bot) -> None:
    #users = await db.get_all_users()
    #for user in users:
        #if user.subscription == 0 and (datetime.today().date() - timedelta(days=1)) == user.subscription_expiry.date():
            # Kick user
            #await bot.send_message(chat_id=user.id, text="Ваша подписка на канал Style by Inna закончилась. Чтобы возобновить подписку - нажмите на кнопку ниже 👇🏻")
            #await bot.ban_chat_member(chat_id=GROUP_ID, user_id=user.id)
            #await bot.unban_chat_member(chat_id=GROUP_ID, user_id=user.id)


async def check_and_update_subscriptions(bot: Bot) -> None:
    users = await db.get_all_users()
    for user in users:
        if user.subscription_expiry.date() == (datetime.today().date() - timedelta(days=1)) and user.balance >= SUBSCRIPTION_PRICE:
            await bot.send_message(chat_id=user.id, text=f"Ваша подписка на канал Style by Inna продлена на 1 месяц. Со счёта списано {SUBSCRIPTION_PRICE}₽\n\nПодписка активна до {(user.subscription_expiry + timedelta(days=SUBSCRIPTION_PERIOD)).strftime('%d.%m.%Y')}")
            await db.update_subscription(user_id=user.id)
        elif user.subscription_expiry.date() == (datetime.today().date() + timedelta(days=3)) and user.balance < SUBSCRIPTION_PRICE:
            await send_remainder(user_id=user.id, bot=bot)
        elif user.subscription_expiry.date() <= (datetime.today().date() - timedelta(days=1)):
            await db.disable_subscription(user_id=user.id)
    users = await db.get_all_users()
    for user in users:
        if user.subscription == 0 and (datetime.today().date() - timedelta(days=1)) == user.subscription_expiry.date():
            # Kick user
            await bot.send_message(chat_id=user.id, text="Ваша подписка на канал Style by Inna закончилась. Чтобы возобновить подписку - нажмите на кнопку ниже 👇🏻")
            await bot.ban_chat_member(chat_id=GROUP_ID, user_id=user.id)
            await bot.unban_chat_member(chat_id=GROUP_ID, user_id=user.id)
