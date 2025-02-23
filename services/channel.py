from aiogram import Bot
from config import GROUP_ID
from aiogram.exceptions import TelegramBadRequest


async def is_user_in_channel(user_id: str, bot: Bot) -> bool:
    print('Checking is there user in channel...')
    result = await bot.get_chat_member(chat_id=GROUP_ID, user_id=user_id)
    if result.status != 'kicked' and result.status != 'left':
        return True
    else:
        return False