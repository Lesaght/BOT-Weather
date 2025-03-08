import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)

ACCUWEATHER_API_KEY = "ACCUWEATHER_API_KEY"
TELEGRAM_TOKEN = "TELEGRAM_TOKEN_BOT"

# Локализованные тексты
TEXTS = {
    "ru": {
        "start": (
            "⛅ Добро пожаловать в Погодный Бот!\n"
            "Отправьте мне название города, и я пришлю:\n"
            "- Текущую погоду\n"
            "- Рекомендации по активностям\n"
            "- Советы по одежде\n"
            "- УФ-индекс и качество воздуха"
        ),
        "input_city": "🌍 Введите название города:",
        "city_not_found": "🚫 Город не найден",
        "weather_error": "😢 Не удалось получить данные о погоде",
        "data_error": "⚠️ Ошибка обработки данных",
        "uv_index": {
            0: "🟢 Низкий (без защиты)",
            1: "🟡 Умеренный (SPF 15+)",
            2: "🟠 Высокий (SPF 30+)",
            3: "🔴 Опасный (избегайте солнца)"
        },
        "activities": {
            "clear": "🌞 Ясная погода идеальна для:\n- Пляжного отдыха\n- Велосипедных прогулок\n- Пикника",
            "rain": "🌧️ В дождь лучше:\n- Посетить музей\n- Почитать книгу\n- Устроить киновечер",
            "cloudy": "⛅ При облачности:\n- Прогулка в парке\n- Экскурсия\n- Фотосессия",
            "snow": "❄️ Зимние активности:\n- Катание на лыжах\n- Лепка снеговика\n- Горячий шоколад",
            "fog": "🌫️ В туман:\n- Посещение спа\n- Ароматный кофе\n- Настольные игры",
            "storm": "⛈️ При грозе:\n- Домашний уют\n- Просмотр сериалов\n- Приготовление выпечки"
        },
        "clothes": {
            "hot": "👕 Легкая одежда:\nШорты/юбка + футболка\nСолнцезащитные очки",
            "warm": "🧥 Умеренная температура:\nДжинсы + рубашка\nЛегкая ветровка",
            "cool": "🧣 Прохладная погода:\nСвитер + брюки\nДемисезонная куртка",
            "cold": "🧤 Холодно:\nТермобелье\nПуховик\nШапка и шарф"
        },
        "history": "📜 История поиска:\n{}",
        "empty_history": "📭 История поиска пуста",
        "help": "❓ Помощь:\nОтправьте мне название города или используйте кнопки ниже",
        "menu": "👇 Выберите действие:",
        "language": "🇷🇺 Русский",
        "language_changed": "🌐 Язык изменен на Русский",
        "temperature": "Температура",
        "condition": "Состояние",
        "wind": "Ветер",
        "recommendations": "Рекомендации",
        "clothing": "Одежда"
    },
    "en": {
        "start": (
            "⛅ Welcome to Weather Bot!\n"
            "Send me a city name and I'll provide:\n"
            "- Current weather\n"
            "- Activity recommendations\n"
            "- Clothing advice\n"
            "- UV index and air quality"
        ),
        "input_city": "🌍 Enter city name:",
        "city_not_found": "🚫 City not found",
        "weather_error": "😢 Failed to get weather data",
        "data_error": "⚠️ Data processing error",
        "uv_index": {
            0: "🟢 Low (no protection)",
            1: "🟡 Moderate (SPF 15+)",
            2: "🟠 High (SPF 30+)",
            3: "🔴 Dangerous (avoid sun)"
        },
        "activities": {
            "clear": "🌞 Clear weather is perfect for:\n- Beach time\n- Cycling\n- Picnic",
            "rain": "🌧️ Rainy day activities:\n- Visit museum\n- Read a book\n- Movie night",
            "cloudy": "⛅ Cloudy weather ideas:\n- Park walk\n- City tour\n- Photo session",
            "snow": "❄️ Winter activities:\n- Skiing\n- Build a snowman\n- Hot chocolate",
            "fog": "🌫️ Foggy day:\n- Spa visit\n- Coffee break\n- Board games",
            "storm": "⛈️ Stormy weather:\n- Stay home\n- Watch movies\n- Bake cookies"
        },
        "clothes": {
            "hot": "👕 Light clothes:\nShorts/skirt + t-shirt\nSunglasses",
            "warm": "🧥 Moderate weather:\nJeans + shirt\nLight jacket",
            "cool": "🧣 Cool weather:\nSweater + pants\nFall jacket",
            "cold": "🧤 Cold weather:\nThermal wear\nDown coat\nHat and scarf"
        },
        "history": "📜 Search history:\n{}",
        "empty_history": "📭 History is empty",
        "help": "❓ Help:\nSend me a city name or use buttons below",
        "menu": "👇 Choose action:",
        "language": "🇬🇧 English",
        "language_changed": "🌐 Language changed to English",
        "temperature": "Temperature",
        "condition": "Condition",
        "wind": "Wind",
        "recommendations": "Recommendations",
        "clothing": "Clothing"
    }
}

MENU_KEYBOARD = {
    "ru": InlineKeyboardMarkup([
        [InlineKeyboardButton("🌤️ Узнать погоду", callback_data='get_weather')],
        [InlineKeyboardButton("📜 История", callback_data='show_history')],
        [InlineKeyboardButton("❓ Помощь", callback_data='help'),
         InlineKeyboardButton("🌐 Язык", callback_data='change_language')]
    ]),
    "en": InlineKeyboardMarkup([
        [InlineKeyboardButton("🌤️ Get Weather", callback_data='get_weather')],
        [InlineKeyboardButton("📜 History", callback_data='show_history')],
        [InlineKeyboardButton("❓ Help", callback_data='help'),
         InlineKeyboardButton("🌐 Language", callback_data='change_language')]
    ])
}

LANGUAGE_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("🇷🇺 Русский", callback_data='ru'),
     InlineKeyboardButton("🇬🇧 English", callback_data='en')],
    [InlineKeyboardButton("🔙 Back", callback_data='back_to_menu')]
])

BACK_KEYBOARD = {
    "ru": InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')]]),
    "en": InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='back_to_menu')]])
}


def get_user_language(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get('language', 'ru')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_language(context)
    await update.message.reply_text(TEXTS[lang]["start"], reply_markup=MENU_KEYBOARD[lang])


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = get_user_language(context)

    if query.data == 'get_weather':
        await query.edit_message_text(TEXTS[lang]["input_city"], reply_markup=BACK_KEYBOARD[lang])
    elif query.data == 'show_history':
        history = context.user_data.get('history', [])
        if history:
            text = TEXTS[lang]["history"].format("\n".join(f"• {city.capitalize()}" for city in reversed(history[-5:])))
        else:
            text = TEXTS[lang]["empty_history"]
        await query.edit_message_text(text, reply_markup=BACK_KEYBOARD[lang])
    elif query.data == 'help':
        await query.edit_message_text(TEXTS[lang]["help"], reply_markup=BACK_KEYBOARD[lang])
    elif query.data == 'change_language':
        await query.edit_message_text("🌐 Choose language:", reply_markup=LANGUAGE_KEYBOARD)
    elif query.data in ['ru', 'en']:
        context.user_data['language'] = query.data
        lang = query.data
        await query.edit_message_text(TEXTS[lang]["language_changed"], reply_markup=MENU_KEYBOARD[lang])
    elif query.data == 'back_to_menu':
        await query.edit_message_text(TEXTS[lang]["menu"], reply_markup=MENU_KEYBOARD[lang])


def get_location_key(city: str):
    try:
        url = "http://dataservice.accuweather.com/locations/v1/cities/search"
        params = {
            "apikey": ACCUWEATHER_API_KEY,
            "q": city,
            "language": "ru-ru"
        }
        response = requests.get(url, params=params)
        return response.json()[0]["Key"]
    except:
        return None


def get_weather_data(location_key: str):
    try:
        url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}"
        params = {
            "apikey": ACCUWEATHER_API_KEY,
            "details": True,
            "language": "ru-ru"
        }
        response = requests.get(url, params=params)
        return response.json()[0]
    except:
        return None


def generate_report(city: str, weather: dict, lang: str):
    try:
        # Безопасный доступ к данным
        temp_data = weather.get("Temperature", {}).get("Metric", {})
        temp = temp_data.get("Value", "N/A")

        condition = weather.get("WeatherText", "N/A").lower()

        wind_data = weather.get("Wind", {}).get("Speed", {}).get("Metric", {})
        wind = wind_data.get("Value", "N/A")

        uv_value = weather.get("UVIndex", 0)
        uv = min(int(uv_value) // 3, 3) if isinstance(uv_value, (int, float)) else 0

        icon = weather.get("WeatherIcon", 0)

        # Определение активности
        activity_key = "clear"
        if any(word in condition for word in ["rain", "дождь", "storm", "гроза"]):
            activity_key = "rain"
        elif any(word in condition for word in ["snow", "снег"]):
            activity_key = "snow"
        elif 6 <= icon <= 11:
            activity_key = "cloudy"
        elif icon > 11:
            activity_key = "fog"

        # Рекомендации по одежде
        try:
            temp = float(temp)
            if temp >= 25:
                clothes_key = "hot"
            elif 18 <= temp < 25:
                clothes_key = "warm"
            elif 5 <= temp < 18:
                clothes_key = "cool"
            else:
                clothes_key = "cold"
        except:
            clothes_key = "cold"

        # Формирование отчета
        report = (
            f"📍 {city.capitalize()}\n\n"
            f"🌡 {TEXTS[lang].get('temperature', 'Temperature')}: {temp}°C\n"
            f"🌀 {TEXTS[lang].get('condition', 'Condition')}: {condition.capitalize()}\n"
            f"💨 {TEXTS[lang].get('wind', 'Wind')}: {wind} km/h\n"
            f"🕶 {TEXTS[lang].get('uv_index', 'UV Index')}: {TEXTS[lang]['uv_index'].get(uv, 'N/A')}\n\n"
            f"🎯 {TEXTS[lang].get('recommendations', 'Recommendations')}:\n{TEXTS[lang]['activities'].get(activity_key, '')}\n\n"
            f"👚 {TEXTS[lang].get('clothing', 'Clothing')}:\n{TEXTS[lang]['clothes'].get(clothes_key, '')}"
        )
        return report

    except Exception as e:
        print(f"[Ошибка] generate_report: {str(e)}")
        raise KeyError("Data processing error")


async def handle_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_language(context)
    city = update.message.text.strip().lower()

    # Сохраняем в историю
    context.user_data.setdefault('history', [])
    context.user_data['history'] = [city] + context.user_data['history'][:9]  # Последние 10 записей

    try:
        if location_key := get_location_key(city):
            if weather_data := get_weather_data(location_key):
                report = generate_report(city, weather_data, lang)
                await update.message.reply_text(report, reply_markup=MENU_KEYBOARD[lang])
            else:
                await update.message.reply_text(TEXTS[lang]["weather_error"], reply_markup=MENU_KEYBOARD[lang])
        else:
            await update.message.reply_text(TEXTS[lang]["city_not_found"], reply_markup=MENU_KEYBOARD[lang])
    except KeyError:
        await update.message.reply_text(TEXTS[lang]["data_error"], reply_markup=MENU_KEYBOARD[lang])
    except Exception as e:
        print(f"[Критическая ошибка] handle_weather: {str(e)}")
        await update.message.reply_text("⚠️ Произошла внутренняя ошибка", reply_markup=MENU_KEYBOARD[lang])


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_weather))
    print("✅ Bot started!")
    app.run_polling()


if __name__ == "__main__":
    main()