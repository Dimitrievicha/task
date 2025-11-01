import os
import asyncio
import logging
from telegram.ext import Application, CommandHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Токены всех ботов
BOT_TOKENS = {
    "bot1": os.environ.get("BOT1_TOKEN"),
    "bot2": os.environ.get("BOT2_TOKEN"),
    "bot3": os.environ.get("BOT3_TOKEN"),
    "bot4": os.environ.get("BOT4_TOKEN"),
    "bot5": os.environ.get("BOT5_TOKEN"),
    "bot6": os.environ.get("BOT6_TOKEN"),
}


async def run_bot(token: str, bot_name: str):
    """Запуск одного бота"""
    if not token:
        print(f"❌ Токен для {bot_name} не установлен")
        return

    app = Application.builder().token(token).build()

    # Команды для бота
    async def start(update, context):
        await update.message.reply_text(f"Я {bot_name}! 🚀")

    async def help(update, context):
        await update.message.reply_text(f"Это помощь для {bot_name}")

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))

    print(f"✅ {bot_name} запущен")
    await app.run_polling()


async def main():
    """Запуск всех ботов"""
    tasks = []

    for bot_name, token in BOT_TOKENS.items():
        if token:  # Запускаем только если токен установлен
            task = run_bot(token, bot_name)
            tasks.append(task)

    if tasks:
        print(f"🚀 Запускаю {len(tasks)} ботов...")
        await asyncio.gather(*tasks)
    else:
        print("❌ Не найдено ни одного токена для запуска")


if __name__ == "__main__":
    asyncio.run(main())