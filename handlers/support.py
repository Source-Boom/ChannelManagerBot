from aiogram import Router, F, Bot
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from config import SUPPORT_CHAT_ID
from keyboards.main import back_button, start_menu

from db.crud import db

import traceback

router = Router()


class Question(StatesGroup):
    waiting_for_question = State()


@router.message(F.text == "Задать вопрос")
async def cmd_ask_question(message: Message, state: FSMContext):
    await state.set_state(Question.waiting_for_question)
    await message.answer(text="Задавайте свой вопрос, а я передам его менеджеру!", reply_markup=back_button)

async def create_topic(bot: Bot, chat_id: int, name: str, user_id: int) -> int:
    try:
        topic_id = await db.get_topic_by_user_id(user_id=user_id)
        if topic_id is None:
            forum_topic = await bot.create_forum_topic(chat_id=chat_id, name=name)
            topic_id = forum_topic.message_thread_id
            await db.create_topic_for_user(user_id=user_id, topic_id=topic_id)
        return topic_id
    except Exception as e:
        traceback.print_exc()
        print(f'Error: {e}')



@router.message(Question.waiting_for_question)
async def cmd_transfer_question(message: Message, state: FSMContext):
    current_state = await state.get_state()
    user = message.from_user
    if current_state == Question.waiting_for_question.state:
        if message.text != 'Назад':
            if user.username is not None:
                need_name = user.username
            else:
                need_name = user.first_name
            topic_id = await create_topic(
                bot=message.bot, 
                chat_id=SUPPORT_CHAT_ID, 
                name=need_name,
                user_id=user.id
            )

            support_msg = await message.bot.copy_message(
                chat_id=SUPPORT_CHAT_ID,
                message_thread_id=topic_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )

            await db.store_user_support_message(support_msg.message_id, message.from_user.id)

            await state.clear()
            await message.answer(text='Сообщение отправлено менеджеру! Скоро будет ответ.', reply_markup=start_menu)




@router.message()
async def cmd_reply_user_message(message: Message, bot: Bot):
    if message.chat.id == SUPPORT_CHAT_ID and message.message_thread_id != None and message.id != message.message_thread_id:
        user_id = await db.get_user_id_by_topic(message.message_thread_id)
        if user_id:
            if message.photo is not None or message.document is not None:
                caption = '👨‍💼 Ответ от поддержки' + ('\n\n' + message.caption if message.caption is not None else '')
                s_msg = await message.bot.copy_message(
                    chat_id=user_id,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id,
                    caption=caption
                )
            else:
                msg_text = '👨‍💼 Ответ от поддержки\n\n' + message.text
                s_msg = await message.bot.send_message(
                    chat_id=user_id,
                    text=msg_text
                )
            await message.bot.send_message(
                chat_id=message.chat.id,
                text="Ответ успешно отправлен!",
                reply_to_message_id=message.message_id  # Указываем ID сообщения, на которое отвечаем
            )
        else:
            await message.reply("Ошибка: не найден исходный пользователь.")