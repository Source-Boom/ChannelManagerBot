from aiogram import Router, F
from aiogram.types import Message
from keyboards.main import start_menu, lawyer_menu
from config import GROUP_ID


router = Router()


@router.message(lambda cmd: cmd.text == '/start' or cmd.text == 'Назад')
async def cmd_start(message: Message):
    await message.answer(text='''Добро пожаловать в чат стиля!\n\nЗдесь Вы сможете подписаться на закрытый тг канал, который поможет Вам всегда быть в курсе трендов мира моды. Также я научу Вас работать с Вашей внешностью, предложу варианты одежды, подходящие именно Вашим пропорциям.\n\nНажимайте на кнопку Подписка и следуйте инструкции 👇🏻''', 
                         reply_markup=start_menu)


@router.message(F.text == 'Юр. информация')
async def cmd_juristic_info(message: Message):
    await message.answer(text="Немного юридической информации с ссылками", reply_markup=lawyer_menu)


# @router.message(F.text == '/id')
# async def cmd_print_group_id(message: Message):
#     '''
#     Вспомогательная функция для получения ID группы. Выдает результат в консоль
#     '''
#     group_id = await message.bot.get_chat('@cucucz')
#     print(f'Group ID: {group_id.id}')