import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = "8213746380:AAHn75hYRMGkeB9sbxyMdzrREwT6jtn4kt8"

# Ссылка на следующего бота
NEXT_BOT_LINK = "@Lyka_ask_bot"

# Состояния пользователей
user_states = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user_id = update.effective_user.id

    start_text = (
        "Мне очень лень проводить тебе что-то сложное. "
        "Давай ты просто за три попытки постараешься угадать какое я задумал число ха-ха-ха"
    )

    # Отправляем начальное сообщение с кнопкой
    keyboard = [[InlineKeyboardButton("Ок, давай попробую", callback_data="start_game")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.message.reply_text(start_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(start_text, reply_markup=reply_markup)


async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    """Начинает игру"""
    # Генерируем случайное число от 0 до 200
    secret_number = random.randint(0, 200)

    # Инициализируем состояние пользователя
    user_states[user_id] = {
        "secret_number": secret_number,
        "attempts_left": 10,
        "game_active": True,
        "last_guess": None
    }

    game_start_text = (
        f"Я загадал число от 0 до 200!\n"
        f"У тебя есть 10 попыток, чтобы угадать.\n"
        f"Попыток осталось: {user_states[user_id]['attempts_left']}\n\n"
    )

    if update.callback_query:
        await update.callback_query.message.reply_text(game_start_text)
    else:
        await update.message.reply_text(game_start_text)


async def handle_guess(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик угадывания числа"""
    user_id = update.effective_user.id

    # Проверяем, активна ли игра у пользователя
    if user_id not in user_states or not user_states[user_id]["game_active"]:
        await update.message.reply_text("Начни игру с помощью команды /start")
        return

    user_state = user_states[user_id]

    # Проверяем, что сообщение содержит число
    try:
        guess = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("Пожалуйста, введи целое число!")
        return

    # Проверяем диапазон числа
    if guess < 0 or guess > 200:
        await update.message.reply_text("Число должно быть от 0 до 200!")
        return

    # Уменьшаем количество попыток
    user_state["attempts_left"] -= 1
    user_state["last_guess"] = guess

    secret_number = user_state["secret_number"]

    # Проверяем, угадал ли пользователь
    if guess == secret_number:
        await win_game(update, user_id)
        return

    # Даем подсказку "горячо/холодно"
    hint = get_temperature_hint(guess, secret_number, user_state.get("last_guess"))

    # Проверяем, остались ли попытки
    if user_state["attempts_left"] <= 0:
        await lose_game(update, user_id)
        return

    # Продолжаем игру
    game_continue_text = (
        f"{hint}\n"
        f"Попыток осталось: {user_state['attempts_left']}\n"
        "Попробуй еще раз:"
    )

    await update.message.reply_text(game_continue_text)


def get_temperature_hint(current_guess: int, secret_number: int, last_guess: int) -> str:
    """Возвращает подсказку 'горячо/холодно'"""
    difference = abs(current_guess - secret_number)

    if difference == 0:
        return "🎯 Ты угадал!"
    elif difference <= 5:
        return "🔥 Очень горячо!"
    elif difference <= 15:
        return "🔥 Горячо"
    elif difference <= 30:
        return "💚 Тепло"
    elif difference <= 50:
        return "💙 Прохладно"
    elif difference <= 80:
        return "❄️ Холодно"
    else:
        return "🧊 Очень холодно!"


async def win_game(update: Update, user_id: int) -> None:
    """Обработчик победы"""
    user_state = user_states[user_id]
    user_state["game_active"] = False

    win_text = (
        'А ты удачливый, ну ладно код "=", и вот ссылка на еще одного братана ха ха ха!\n'
        f"{NEXT_BOT_LINK}"
    )

    await update.message.reply_text(win_text)


async def lose_game(update: Update, user_id: int) -> None:
    """Обработчик проигрыша"""
    user_state = user_states[user_id]
    secret_number = user_state["secret_number"]
    user_state["game_active"] = False

    lose_text = (
        f"💀 Не повезло, я загадал {secret_number}!\n\n"
        "Будешь еще пробовать?"
    )

    # Кнопка для перезапуска игры
    keyboard = [[InlineKeyboardButton("Да", callback_data="restart_game")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(lose_text, reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # Обработка кнопки "Ок, давай попробую"
    if query.data == "start_game":
        await start_game(update, context, user_id)
        return

    # Обработка кнопки "Да" для перезапуска игры
    if query.data == "restart_game":
        await start_game(update, context, user_id)
        return


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    help_text = """
🤖 Команды бота:
/start - Начать игру
/help - Показать эту справку

🎮 Правила игры:
• Я загадываю число от 0 до 200
• У тебя 5 попыток, чтобы угадать
• После каждой попытки я подскажу "горячо" или "холодно"
    """
    await update.message.reply_text(help_text)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений"""
    user_id = update.effective_user.id

    # Если пользователь в игре, обрабатываем как попытку угадать
    if user_id in user_states and user_states[user_id]["game_active"]:
        await handle_guess(update, context)
    else:
        await update.message.reply_text("Используй /start чтобы начать игру или /help для справки.")


def main() -> None:
    """Основная функция запуска бота"""
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler, pattern="^(start_game|restart_game)"))

    # Обработчик для текстовых сообщений (угадывание чисел)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Бот 'Угадай число' запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()