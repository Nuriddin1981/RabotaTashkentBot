import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.filters import Command

API_URL = "https://api.hh.ru/vacancies"
BOT_TOKEN = "7585396447:AAGH_1JwiNqbvHfjvjQTfqnrRq7sH7XAbVs"  # Заменить на реальный токен

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Фильтры вакансий
CITIES = {
    "Москва": 1, "Санкт-Петербург": 2, "Новосибирск": 4, "Казань": 88, "Екатеринбург": 3,
    "Челябинск": 104, "Уфа": 99, "Ростов-на-Дону": 76, "Нижний Новгород": 66, "Самара": 78
}
SALARIES = [50000, 100000, 150000]
EXPERIENCE = {"Без опыта": "noExperience", "1-3 года": "between1And3", "3-5 лет": "between3And6"}
EMPLOYMENT = {"Полная": "full", "Частичная": "part", "Удалёнка": "remote"}
INDUSTRIES = {"IT": "1", "Маркетинг": "2", "Продажи": "3"}

# Состояние пользователя
user_filters = {}

def create_keyboard(options, prefix):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=key, callback_data=f"{prefix}:{value}")]
        for key, value in options.items()
    ])
    return keyboard

@dp.message(Command("start"))
async def start(message: Message):
    keyboard = create_keyboard(CITIES, "city")
    await message.answer("Выберите город:", reply_markup=keyboard)

@dp.callback_query()
async def handle_callback(callback: CallbackQuery):
    data = callback.data.split(":")
    if len(data) == 2:
        key, value = data
        user_filters[key] = value
        await callback.answer(f"Выбрано: {key} - {value}")
        
        if key == "city":
            keyboard = create_keyboard(EXPERIENCE, "exp")
            await callback.message.answer("Выберите опыт:", reply_markup=keyboard)
        elif key == "exp":
            keyboard = create_keyboard(EMPLOYMENT, "emp")
            await callback.message.answer("Выберите тип занятости:", reply_markup=keyboard)
        elif key == "emp":
            await send_vacancies(callback.message)

async def send_vacancies(message: Message):
    city = user_filters.get("city", "1")
    exp = user_filters.get("exp", "noExperience")
    emp = user_filters.get("emp", "full")
    url = f"{API_URL}?area={city}&experience={exp}&employment={emp}&per_page=10"
    response = requests.get(url)
    data = response.json()
    vacancies = data.get("items", [])

    if vacancies:
        for vac in vacancies:
            text = f"<b>{vac['name']}</b>\n{vac['alternate_url']}"
            await message.answer(text, parse_mode=ParseMode.HTML)
    else:
        await message.answer("Вакансий не найдено.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
