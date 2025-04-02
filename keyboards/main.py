from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import INVITATION_LINK

start_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Подписка")],
        [KeyboardButton(text="Задать вопрос"), KeyboardButton(text="Юр. информация")],
        [KeyboardButton(text="Правила чата")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

subscription_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Оформить подписку", callback_data="replenish")]
    ]
)

subscription_menu_active = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Пополнить счёт", callback_data="replenish")]
    ]
)


back_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


lawyer_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Договор оферты', url='https://disk.yandex.ru/i/3YpNqna5NCXCqQ')],
        [InlineKeyboardButton(text='Политика конфиденциальности', url='https://disk.yandex.ru/d/Pw9zAOCqQJMovA')]
    ]
)

invtitation_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Перейти в канал', url=INVITATION_LINK)]
    ]
)