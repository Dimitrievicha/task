import logging
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = "7704700673:AAFxkPbz8jjLziEIaidYvxh9Z_rBiJgqhbo"

# ========== ВОПРОСЫ КВИЗА ==========
QUESTIONS = [
    {
        "question": "По знаку зодиака Дима скорпион, а в асценденте кто он?",
        "options": ["Скорпион", "Телец", "Рыбы", "Весы"],
        "correct": 0
    },
    {
        "question": "Как зовут любимую кошку Димы?",
        "options": ["Кола", "Фанта", "Пепси", "Липтон"],
        "correct": 2
    },
    {
        "question": "Получал ли когда либо Дима тройку за сессию?",
        "options": ["Да, в первой же", "Нет, никогда", "Нет, но был на грани"],
        "correct": 2
    },
    {
        "question": "Куда Дима мечтает съездить?",
        "options": ["В Париж", "В Нью-Йорк", "В Карелию", "В Лондон"],
        "correct": 1
    },
    {
        "question": "Какой продукт Дима НЕ любит?",
        "options": ["Орехи", "Яйца", "Баклажаны", "Рыбу"],
        "correct": 3
    },
    {
        "question": "Какое зрение у Димы?",
        "options": ["1", "-1", "-1 и астигматизм на оба глаза", "-0.5 на один глаз и астигматизм на другой глаз"],
        "correct": 2
    },
    {
        "question": "Какая любимая песня Димы?",
        "options": ["Терентий", "Аполлинария", "Останусь", "Kukareku"],
        "correct": 2
    },
    {
        "question": "Кем работал Дима?",
        "options": ["Доставка документов", "официант", "уборщик школы", "репетитор"],
        "correct": 0
    },
    {
        "question": "Кем хотел стать в детстве Дима?",
        "options": ["Уборщик", "Продавец Магнита", "Врач", "Пожарный"],
        "correct": 1
    },
    {
        "question": "Что коллекционирует Дима?",
        "options": ["Колокольчики", "Марки", "Монеты", "Открытки"],
        "correct": 0
    }
]

# Ссылка на следующего бота
NEXT_BOT_LINK = "@Rikki_ask_bot"

# Состояния пользователей
user_states = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user_id = update.effective_user.id

    # Отправляем начальное сообщение с кнопкой
    keyboard = [[InlineKeyboardButton("Начать квиз", callback_data="start_quiz")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    start_text = (
        "Хай! Вижу босс тебя отправил сначала ко мне ха ха ха.\n"
        "Мне очень интересно узнать на сколько ты хорошо знаешь Диму ха ха ха\n"
        "Если убедишь, что ты ему настоящий друг, то я дам тебе кусочек кода"
    )

    if update.callback_query:
        await update.callback_query.message.reply_text(start_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(start_text, reply_markup=reply_markup)


async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    """Начинает квиз"""
    # Инициализируем состояние пользователя
    user_states[user_id] = {
        "current_question": 0,
        "correct_answers": 0,
        "questions_order": list(range(len(QUESTIONS))),
        "message_ids": []  # Для хранения ID сообщений с вопросами
    }

    # Перемешиваем вопросы
    random.shuffle(user_states[user_id]["questions_order"])

    await send_question(update, context, user_id)


async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    """Отправляет вопрос пользователю"""
    user_state = user_states[user_id]
    current_q_index = user_state["current_question"]

    if current_q_index >= len(QUESTIONS):
        await show_results(update, context, user_id)
        return

    # Получаем текущий вопрос
    question_index = user_state["questions_order"][current_q_index]
    question_data = QUESTIONS[question_index]

    # Создаем клавиатуру с вариантами ответов
    keyboard = []
    for i, option in enumerate(question_data["options"]):
        keyboard.append([InlineKeyboardButton(option, callback_data=f"answer_{i}")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем вопрос и сохраняем ID сообщения
    if update.callback_query:
        message = await update.callback_query.message.reply_text(
            question_data["question"],
            reply_markup=reply_markup
        )
    else:
        message = await update.message.reply_text(
            question_data["question"],
            reply_markup=reply_markup
        )

    user_state["message_ids"].append(message.message_id)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # Обработка кнопки "Начать квиз"
    if query.data == "start_quiz":
        await start_quiz(update, context, user_id)
        return

    if user_id not in user_states:
        await query.message.reply_text("Начните квиз с помощью команды /start")
        return

    user_state = user_states[user_id]

    # Получаем данные о текущем вопросе
    current_q_index = user_state["current_question"]
    question_index = user_state["questions_order"][current_q_index]
    question_data = QUESTIONS[question_index]

    # Получаем выбранный ответ
    answer_index = int(query.data.split("_")[1])
    selected_answer = question_data["options"][answer_index]

    # Отправляем выбранный ответ как сообщение пользователя
    await query.message.reply_text(f"➤ {selected_answer}")

    # Проверяем правильность ответа
    if answer_index == question_data["correct"]:
        user_state["correct_answers"] += 1

    # Увеличиваем счетчик вопросов
    user_state["current_question"] += 1

    # Отправляем следующий вопрос или результаты
    await send_question(update, context, user_id)


async def show_results(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    """Показывает результаты квиза"""
    user_state = user_states[user_id]
    correct_answers = user_state["correct_answers"]
    total_questions = len(QUESTIONS)

    # Определяем результат
    if correct_answers <= 5:
        message_text = (
            f"🧐 Результат: {correct_answers}/{total_questions}\n\n"
            "Что-то ты совсем Диму плохо знаешь, ладно, дам тебе еще шанс.\n"
            "Квиз начнется заново через 3 секунды..."
        )

        # Отправляем сообщение о результате
        if update.callback_query:
            await update.callback_query.message.reply_text(message_text)
        else:
            await update.message.reply_text(message_text)

        # Ждем 3 секунды и автоматически перезапускаем квиз
        await asyncio.sleep(3)
        await start_quiz(update, context, user_id)

    elif 6 <= correct_answers <= 8:
        message_text = (
            f"😏 Результат: {correct_answers}/{total_questions}\n\n"
            "Ну не плохо. Ладно, вот тебе кусочек кода \"СЧА\" и ссылка на следующего дружка ха-ха-ха.\n"
            "Думал все будет так просто? Ладно, времени с тобой общаться у меня нет. Проваливай!\n\n"
            f"Ссылка: {NEXT_BOT_LINK}"
        )
        # Очищаем состояние после хорошего результата
        user_states[user_id] = {}

        if update.callback_query:
            await update.callback_query.message.reply_text(message_text)
        else:
            await update.message.reply_text(message_text)
    else:  # 9-10
        message_text = (
            f"🎉 Результат: {correct_answers}/{total_questions}\n\n"
            "Браво! Возьми пирожок с полки.\n"
            "Вот тебе кусочек кода \"СЧА\" и ссылка на следующего дружка ха-ха-ха.\n"
            "Думал все будет так просто? Ладно, времени с тобой общаться у меня нет. Проваливай!\n\n"
            f"Ссылка: {NEXT_BOT_LINK}"
        )
        # Очищаем состояние после отличного результата
        user_states[user_id] = {}

        if update.callback_query:
            await update.callback_query.message.reply_text(message_text)
        else:
            await update.message.reply_text(message_text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    help_text = """
🤖 Команды бота:
/start - Начать квиз
/help - Показать эту справку

📝 О квизе:
• 10 вопросов о Диме
• Выбирайте ответы с помощью кнопок
• Узнайте насколько хорошо вы знаете Диму!
    """
    await update.message.reply_text(help_text)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений (игнорирует все кроме команд)"""
    user_id = update.effective_user.id

    # Если пользователь проходит квиз, напоминаем использовать кнопки
    if user_id in user_states:
        await update.message.reply_text("Пожалуйста, выбирайте ответы с помощью кнопок под вопросами.")
    else:
        await update.message.reply_text("Используйте /start чтобы начать квиз или /help для справки.")


def main() -> None:
    """Основная функция запуска бота"""
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler, pattern="^(start_quiz|answer_.*)$"))

    # Обработчик для текстовых сообщений (игнорирует все)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Бот-квиз запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()