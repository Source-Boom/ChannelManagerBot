from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.main import subscription_menu, invtitation_button
from config import SUBSCRIPTION_PRICE

from services.channel import is_user_in_channel
from db.crud import db

from datetime import datetime

router = Router()


@router.message(F.text == 'Подписка')
async def cmd_ask(message: Message):
    user_id = message.from_user.id

    if await db.is_user(user_id=user_id):
        user_balance = await db.get_balance(user_id) 
        user_subscription_expiry = await db.get_subscription_expiry(user_id=user_id)
        if await db.is_user_subscription_active(user_id):
            await message.answer(text=f"Стоимость подписки: {SUBSCRIPTION_PRICE}р\n\nВаш баланс: {user_balance}р\nПодписка активна до {user_subscription_expiry.date()}", 
                                        reply_markup=subscription_menu)
        else:
            await message.answer(text=f'Стоимость подписки: {SUBSCRIPTION_PRICE}р\n\nВаша подписка неактивна. Пополните баланс для активации',
                                 reply_markup=subscription_menu)
    else:
        await message.answer(text=f'Стоимость подписки: {SUBSCRIPTION_PRICE}р\n\nВаша подписка неактивна. Пополните баланс для активации',
                             reply_markup=subscription_menu)
    

#
# Дописать оплату
#
from payment.core import process_payment


@router.callback_query(lambda cmd: cmd.data.startswith("replenish"))
async def cmd_replenish(callback: CallbackQuery):
    user_id = callback.from_user.id

    is_payment_successfull = await process_payment(user_id=user_id)

    if is_payment_successfull:

        if not await db.is_user(user_id):
            await db.add_user(user_id)
        
        await db.replenish_user_balance(user_id)

        if not await db.is_user_subscription_active(user_id):
            await db.update_subscription(user_id)
        
        await callback.message.answer(text="Баланс успешно пополнен!")
        try:
            if not await is_user_in_channel(user_id, callback.message.bot):
                await callback.message.answer(text='Ссылка на вход в канал', reply_markup=invtitation_button)
        except:
            print('An error occurred')

