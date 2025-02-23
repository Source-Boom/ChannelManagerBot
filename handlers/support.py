from aiogram import Router, F, Bot
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from config import SUPPORT_CHAT_ID
from keyboards.main import back_button, start_menu

from db.crud import db

router = Router()


class Question(StatesGroup):
    waiting_for_question = State()


@router.message(F.text == "Задать вопрос")
async def cmd_ask_question(message: Message, state: FSMContext):
    await state.set_state(Question.waiting_for_question)
    await message.answer(text="Задавайте свой вопрос, а я передам его менеджеру!", reply_markup=back_button)


@router.message(Question.waiting_for_question)
async def cmd_transfer_question(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == Question.waiting_for_question.state:
        if not message.from_user.username.startswith('Назад'):
            
            support_msg = await message.bot.copy_message(
                chat_id=SUPPORT_CHAT_ID,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )

            await db.store_user_support_message(support_msg.message_id, message.from_user.id)

            await state.clear()
            await message.answer(text='Сообщение отправлено менеджеру! Скоро будет ответ.', reply_markup=start_menu)


@router.message()
async def cmd_reply_user_message(message: Message, bot: Bot):
    if message.chat.id == SUPPORT_CHAT_ID and message.reply_to_message:
        replied_msg_id = message.reply_to_message.message_id
        user_id = await db.get_user_id_by_support_message(replied_msg_id)
        if user_id:
            await bot.send_message(user_id, f"👨‍💼 Ответ от поддержки")
            await message.bot.copy_message(chat_id=user_id,
                                           from_chat_id=message.chat.id,
                                           message_id=message.message_id
                                           )
        else:
            await message.reply("Ошибка: не найден исходный пользователь.")