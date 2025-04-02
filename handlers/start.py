from aiogram import Router, F
from aiogram.types import Message, Chat
from keyboards.main import start_menu, lawyer_menu
from config import GROUP_ID, TOKEN
from aiogram import Bot

#bot = Bot(token=TOKEN)

router = Router()

async def get_chat_info(bot: Bot, chat_id: int) -> Chat:
    try:
        chat = await bot.get_chat(chat_id)
        return chat
    except Exception as e:
        print(f"Ошибка при получении информации о чате: {e}")
        return None

@router.message(lambda cmd: cmd.text == '/start' or cmd.text == 'Назад')
async def cmd_start(message: Message):
    #chat_id = 469998728  # Замените на нужный ID чата
    #chat_info = await get_chat_info(bot, chat_id)
    
    #if chat_info:
        #print(f"Информация о чате: {chat_info}")
    #else:
        #print("Не удалось получить информацию о чате.")
    await message.answer(text='''Добро пожаловать в чат стиля!\n\nЗдесь Вы сможете подписаться на закрытый тг канал, который поможет Вам всегда быть в курсе трендов мира моды. Также я научу Вас работать с Вашей внешностью, предложу варианты одежды, подходящие именно Вашим пропорциям.\n\nНажимайте на кнопку Подписка и следуйте инструкции 👇🏻''', 
                         reply_markup=start_menu)


@router.message(F.text == 'Юр. информация')
async def cmd_juristic_info(message: Message):
    await message.answer(text="Немного юридической информации с ссылками", reply_markup=lawyer_menu)


@router.message(F.text == 'Правила чата')
async def chat_rules(message: Message):
    await message.answer(text="Приветствую Вас в боте, который поможет оформить подписку на закрытый канал о стиле. 👋🏻\n\nСтоимость подписки на месяц 📅составляет 4.990₽.\nПосле оплаты бот пришлёт ссылку 📩 на вступление в чат, нажав на которую, Вы попадёте в закрытый канал.\n\nПодписка действует один месяц, за 3 дня до ее окончания бот напоминает о необходимости продлить.\n\nЧат защищён от копирования и пересылки информации.\n\nВ конце месяца будет опубликован анонс на следующий месяц.\n\nНадеемся, что подписка на закрытый канал принесёт вам приятные эмоции и полезные знания, а также будет местом вашего отдыха и совершенствования себя.\n\nЕсли у Вас возникли вопросы, Вы всегда можете обратиться в поддержку - Задать вопрос в боте.")


# @router.message(F.text == '/id')
# async def cmd_print_group_id(message: Message):
#     '''
#     Вспомогательная функция для получения ID группы. Выдает результат в консоль
#     '''
#     group_id = await message.bot.get_chat('@cucucz')
#     print(f'Group ID: {group_id.id}')
