from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.main import subscription_menu, invtitation_button, subscription_menu_active
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
            await message.answer(text=f"Стоимость подписки на месяц: {SUBSCRIPTION_PRICE}₽\n\nВаш счёт: {user_balance}₽\nПодписка активна до {user_subscription_expiry.strftime('%d.%m.%Y')}", 
                                        reply_markup=subscription_menu_active)
        else:
            await message.answer(text=f'Стоимость подписки на месяц: {SUBSCRIPTION_PRICE}₽\n\nВаша подписка неактивна. Воспользуйтесь кнопкой ниже для её активации',
                                 reply_markup=subscription_menu)
    else:
        await message.answer(text=f'Стоимость подписки на месяц: {SUBSCRIPTION_PRICE}₽\n\nВаша подписка неактивна. Воспользуйтесь кнопкой ниже для её активации',
                             reply_markup=subscription_menu)
    

#
# Дописать оплату
#
from payment.core import generate_link


@router.callback_query(lambda cmd: cmd.data.startswith("replenish"))
async def cmd_replenish(callback: CallbackQuery):
    user_id = callback.from_user.id
    payment_id = await db.create_new_payment(user_id=user_id, message_id=callback.id)
    if not await db.is_user_subscription_active(user_id):
        payment_link = generate_link(payment_id, "Оплата подписки на закрытый канал Style by Inna")
        pay_button = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Оплатить подписку', url=payment_link)]
            ]
        )
        await callback.message.answer(text=f"Для оформления подписки на канал Style by Inna осуществите оплату с помощью кнопки ниже", reply_markup=pay_button)
    else:
        payment_link = generate_link(payment_id, "Пополнение счёта для оплаты подписки на канал Style by Inna")
        pay_button = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Пополнить баланс', url=payment_link)]
            ]
        )
        await callback.message.answer(text=f"Для пополнения счёта на сумму {SUBSCRIPTION_PRICE}₽ осуществите оплату с помощью кнопки ниже", reply_markup=pay_button)
    await callback.message.edit_reply_markup(reply_markup=None)
    #if is_payment_successfull:

        #if not await db.is_user(user_id):
            #await db.add_user(user_id)
        
        #await db.replenish_user_balance(user_id)

        #if not await db.is_user_subscription_active(user_id):
            #await db.update_subscription(user_id)
            #await callback.message.answer(text="Оплата прошла успешно!")
            #try:
                #if not await is_user_in_channel(user_id, callback.message.bot):
               # await callback.message.answer(text='Доступ в закрытый тг канал открыт!\n\nПодайте заявку на вступление в него по ссылке ниже. Бот автоматически её одобрит!', reply_markup=invtitation_button)
            #except:
                #print('An error occurred')
        #else:
            #await callback.message.answer(text=f"Оплата прошла успешно!\n\n{SUBSCRIPTION_PRICE}₽ уже зачислены на ваш счёт!\nПри истечении срока текущей подписки {SUBSCRIPTION_PRICE}₽ будут автоматически списаны со счёта")
