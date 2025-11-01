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
BOT_TOKEN = "8388282004:AAGxWoRSN4dP1UK1iPttFI_fK3WUVwMRLrc"

# Утверждения про Диму
STATEMENTS = [
    {
        "statement": "1) Дима был чемпионом ярославской области по каратэ",
        "answer": True
    },
    {
        "statement": "2) Дима участвовал в вокальном номере",
        "answer": True
    },
    {
        "statement": "3) Дима занимался робототехникой",
        "answer": False
    },
    {
        "statement": "4) Дима имеет секретный тг канал, в котором находятся только избранные",
        "answer": False
    },
    {
        "statement": "5) Дима занимался рэкетирством",
        "answer": False
    },
    {
        "statement": "6) Дима сделал арбалет и сломал им чужую подделку",
        "answer": True
    },
    {
        "statement": "7) Дима издевался над человеком в школе",
        "answer": False
    },
    {
        "statement": "8) Дима Любит число 17",
        "answer": False
    },
    {
        "statement": "9) Дима занимался сталкерством",
        "answer": False
    },
    {
        "statement": "10) Дима имел черепашку",
        "answer": True
    }
]

# Состояния пользователей
user_states = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user_id = update.effective_user.id

    start_text = (
        "Сейчас проверим, насколько хорошо ты знаешь Диму!\n"
        "Я буду говорить утверждения, а ты выбирай - Правда это или Ложь.\n\n"
        "Готов проверить свои знания?"
    )

    # Отправляем начальное сообщение с кнопкой
    keyboard = [[InlineKeyboardButton("Начать игру", callback_data="start_game")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.message.reply_text(start_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(start_text, reply_markup=reply_markup)


async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    """Начинает игру"""
    # Перемешиваем утверждения
    shuffled_statements = random.sample(STATEMENTS, len(STATEMENTS))

    # Инициализируем состояние пользователя
    user_states[user_id] = {
        "current_statement": 0,
        "correct_answers": 0,
        "game_active": True,
        "statements": shuffled_statements
    }

    await send_statement(update, context, user_id)


async def send_statement(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    """Отправляет утверждение пользователю"""
    user_state = user_states[user_id]
    current_index = user_state["current_statement"]

    if current_index >= len(user_state["statements"]):
        await finish_game(update, context, user_id)
        return

    # Получаем текущее утверждение
    statement_data = user_state["statements"][current_index]

    # Создаем клавиатуру с вариантами ответов
    keyboard = [
        [InlineKeyboardButton("✅ Правда", callback_data="answer_true")],
        [InlineKeyboardButton("❌ Ложь", callback_data="answer_false")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем утверждение
    if update.callback_query:
        await update.callback_query.message.reply_text(statement_data["statement"], reply_markup=reply_markup)
    else:
        await update.message.reply_text(statement_data["statement"], reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # Обработка кнопки "Начать игру"
    if query.data == "start_game":
        await start_game(update, context, user_id)
        return

    # Обработка кнопки "Попробовать снова"
    if query.data == "restart_game":
        await start_game(update, context, user_id)
        return

    if user_id not in user_states or not user_states[user_id]["game_active"]:
        await query.message.reply_text("Начни игру с помощью команды /start")
        return

    if query.data.startswith("answer_"):
        user_answer = query.data == "answer_true"  # True если Правда, False если Ложь
        await check_answer(update, context, user_id, user_answer)


async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, user_answer: bool) -> None:
    """Проверяет ответ пользователя"""
    user_state = user_states[user_id]
    current_index = user_state["current_statement"]
    statement_data = user_state["statements"][current_index]

    correct_answer = statement_data["answer"]

    # Проверяем правильность ответа
    if user_answer == correct_answer:
        user_state["correct_answers"] += 1

    # Переходим к следующему утверждению
    user_state["current_statement"] += 1

    # Ждем немного перед следующим утверждением
    await asyncio.sleep(1)
    await send_statement(update, context, user_id)


async def finish_game(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    """Завершает игру и показывает результат"""
    user_state = user_states[user_id]
    correct_answers = user_state["correct_answers"]
    total_statements = len(user_state["statements"])

    user_state["game_active"] = False

    if correct_answers >= 8:  # Больше 7 правильных ответов
        win_text = (
            f"Браво, да ты его очень хорошо знаешь!\n"
            f"Правильных ответов: {correct_answers} из {total_statements}\n\n"
            "Ключ: 02.11.2025\n\n"
            "Возвращайся к боссу"
        )
        await update.callback_query.message.reply_text(win_text)
    else:
        lose_text = (
            f"💀 Не, хреновенько ты его знаешь.\n"
            f"Правильных ответов: {correct_answers} из {total_statements}\n\n"
            "Ты меня разочаровал."
        )

        # Кнопка для перезапуска
        keyboard = [[InlineKeyboardButton("Попробовать снова", callback_data="restart_game")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.message.reply_text(lose_text, reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    help_text = """
🤖 Команды бота:
/start - Начать игру "Правда или Ложь"
/help - Показать эту справку

🎯 Правила игры:
• 10 утверждений про Диму
• Выбирай - Правда или Ложь
• Нужно набрать больше 7 правильных ответов
• Утверждения перемешиваются при каждом запуске
    """
    await update.message.reply_text(help_text)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений"""
    user_id = update.effective_user.id

    if user_id in user_states and user_states[user_id]["game_active"]:
        await update.message.reply_text("Пожалуйста, выбирай ответ с помощью кнопок 'Правда' или 'Ложь'.")
    else:
        await update.message.reply_text("Используй /start чтобы начать игру или /help для справки.")


def main() -> None:
    """Основная функция запуска бота"""
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler, pattern="^(start_game|answer_|restart_game)"))

    # Обработчик для текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Бот 'Правда или Ложь' запущен...")
    application.run_polling()


if __name__ == "__main__":
    import asyncio

    main()