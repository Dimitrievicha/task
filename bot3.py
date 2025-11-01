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
BOT_TOKEN = "8016674756:AAFMnoRz7M23WIjknac9uEterl63FR88zfc"

# Ссылка на следующего бота
NEXT_BOT_LINK = "@Dash_ask_bot"

# Состояния пользователей
user_states = {}

# Варианты ходов
CHOICES = ["камень", "ножницы", "бумага"]
WINNING_COMBINATIONS = {
    "камень": "ножницы",
    "ножницы": "бумага",
    "бумага": "камень"
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user_id = update.effective_user.id

    start_text = (
        "Эй ты. Выиграешь меня в камень-ножницы-бумага, тогда я тебе дам то что ты хочешь. "
        "Но учти, еще никто меня не выигрывал ха ха ха"
    )

    # Отправляем начальное сообщение с кнопкой "Начать игру"
    keyboard = [[InlineKeyboardButton("Начать игру", callback_data="start_game")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.message.reply_text(start_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(start_text, reply_markup=reply_markup)


async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    """Начинает игру"""
    # Инициализируем состояние пользователя
    user_states[user_id] = {
        "user_wins": 0,
        "bot_wins": 0,
        "game_active": True
    }

    game_start_text = (
        f"Счет: Ты {user_states[user_id]['user_wins']} - {user_states[user_id]['bot_wins']} Я\n"
        "Играем до 3 побед!"
    )

    await send_game_choice(update, game_start_text)


async def send_game_choice(update: Update, text: str = None) -> None:
    """Отправляет клавиатуру с выбором хода"""
    if text is None:
        text = "Выбери свой ход:"

    keyboard = [
        [InlineKeyboardButton("🪨 Камень", callback_data="choice_камень")],
        [InlineKeyboardButton("✂️ Ножницы", callback_data="choice_ножницы")],
        [InlineKeyboardButton("📄 Бумага", callback_data="choice_бумага")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # Обработка кнопки "Начать игру"
    if query.data == "start_game":
        await start_game(update, context, user_id)
        return

    # Обработка кнопки "А как же код?"
    if query.data == "ask_code":
        await query.message.reply_text('А? Ах, да, "СТЬЕ"')
        return

    # Обработка кнопки "ДА" для перезапуска игры
    if query.data == "restart_game":
        await start_game(update, context, user_id)
        return

    if user_id not in user_states or not user_states[user_id]["game_active"]:
        await query.message.reply_text("Начни игру с помощью команды /start")
        return

    if query.data.startswith("choice_"):
        user_choice = query.data.split("_")[1]
        await play_round(update, context, user_id, user_choice)


async def play_round(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, user_choice: str) -> None:
    """Играет один раунд"""
    user_state = user_states[user_id]

    # Ход бота
    bot_choice = random.choice(CHOICES)

    # Определяем победителя
    if user_choice == bot_choice:
        result = "Ничья!"
        result_emoji = "🤝"
    elif WINNING_COMBINATIONS[user_choice] == bot_choice:
        result = "Ты выиграл этот раунд!"
        result_emoji = "✅"
        user_state["user_wins"] += 1
    else:
        result = "Я выиграл этот раунд!"
        result_emoji = "❌"
        user_state["bot_wins"] += 1

    # Отправляем результат раунда
    round_text = (
        f"Твой ход: {get_emoji(user_choice)} {user_choice}\n"
        f"Мой ход: {get_emoji(bot_choice)} {bot_choice}\n"
        f"{result_emoji} {result}\n\n"
        f"Счет: Ты {user_state['user_wins']} - {user_state['bot_wins']} Я"
    )

    await update.callback_query.message.reply_text(round_text)

    # Проверяем, закончена ли игра
    if user_state["user_wins"] >= 3 or user_state["bot_wins"] >= 3:
        await finish_game(update, context, user_id)
    else:
        await send_game_choice(update)


async def finish_game(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    """Завершает игру и показывает результат"""
    user_state = user_states[user_id]
    user_state["game_active"] = False

    if user_state["user_wins"] >= 3:
        # Пользователь выиграл
        win_text = (
            "Ладно, ты оказался умнее. Вот тебе ссылка на нового челика:\n"
            f"{NEXT_BOT_LINK}"
        )

        keyboard = [[InlineKeyboardButton("А как же код?", callback_data="ask_code")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.message.reply_text(win_text, reply_markup=reply_markup)
    else:
        # Бот выиграл
        lose_text = "Ха! Лузер! Походу Димы тебе не видать!\n\nНу что? Еще раз попробуешь?"

        keyboard = [[InlineKeyboardButton("ДА", callback_data="restart_game")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.message.reply_text(lose_text, reply_markup=reply_markup)


def get_emoji(choice: str) -> str:
    """Возвращает эмодзи для хода"""
    emojis = {
        "камень": "🪨",
        "ножницы": "✂️",
        "бумага": "📄"
    }
    return emojis.get(choice, "")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    help_text = """
🤖 Команды бота:
/start - Начать игру
/help - Показать эту справку

🎮 Правила игры:
• Камень бьет ножницы
• Ножницы бьют бумагу  
• Бумага бьет камень
• Играем до 3 побед!
    """
    await update.message.reply_text(help_text)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений"""
    user_id = update.effective_user.id

    if user_id in user_states and user_states[user_id]["game_active"]:
        await update.message.reply_text("Пожалуйста, выбирай ход с помощью кнопок ниже.")
    else:
        await update.message.reply_text("Используй /start чтобы начать игру или /help для справки.")


def main() -> None:
    """Основная функция запуска бота"""
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler, pattern="^(start_game|choice_|ask_code|restart_game)"))

    # Обработчик для текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Бот 'Камень-ножницы-бумага' запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()