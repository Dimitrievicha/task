# main.py
import os
import asyncio
import logging
from telegram.ext import Application, CommandHandler

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токены ботов
BOT1_TOKEN = os.environ.get("BOT1_TOKEN")
BOT2_TOKEN = os.environ.get("BOT2_TOKEN")
BOT3_TOKEN = os.environ.get("BOT3_TOKEN")


async def run_bot1():
    """Запуск первого бота"""
    app1 = Application.builder().token(BOT1_TOKEN).build()

    # Команды для бота 1
    app1.add_handler(CommandHandler("start", start1))

    logger.info("Бот 1 запущен")
    await app1.run_polling()


async def run_bot2():
    """Запуск второго бота"""
    app2 = Application.builder().token(BOT2_TOKEN).build()

    # Команды для бота 2
    app2.add_handler(CommandHandler("start", start2))

    logger.info("Бот 2 запущен")
    await app2.run_polling()


async def run_bot3():
    """Запуск третьего бота"""
    app3 = Application.builder().token(BOT3_TOKEN).build()

    # Команды для бота 3
    app3.add_handler(CommandHandler("start", start3))

    logger.info("Бот 3 запущен")
    await app3.run_polling()


async def start1(update, context):
    await update.message.reply_text("Я бот 1!")


async def start2(update, context):
    await update.message.reply_text("Я бот 2!")


async def start3(update, context):
    await update.message.reply_text("Я бот 3!")


async def main():
    """Запуск всех ботов одновременно"""
    await asyncio.gather(
        run_bot1(),
        run_bot2(),
        run_bot3()
    )


if __name__ == "__main__":
    asyncio.run(main())