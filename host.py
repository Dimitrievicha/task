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


class BotManager:
    def __init__(self, token: str, bot_name: str):
        self.token = token
        self.bot_name = bot_name
        self.app = None

    async def start(self):
        """Запуск одного бота"""
        if not self.token:
            print(f"❌ Токен для {self.bot_name} не установлен")
            return

        self.app = Application.builder().token(self.token).build()

        # Команды для бота
        async def start_command(update, context):
            await update.message.reply_text(f"Я {self.bot_name}! 🚀")

        async def help_command(update, context):
            await update.message.reply_text(f"Это помощь для {self.bot_name}")

        self.app.add_handler(CommandHandler("start", start_command))
        self.app.add_handler(CommandHandler("help", help_command))

        print(f"✅ {self.bot_name} запущен")

        # Запускаем polling в отдельной задаче
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()

    async def stop(self):
        """Остановка бота"""
        if self.app:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()


async def main():
    """Запуск всех ботов"""
    bots = []

    # Создаем менеджеры для всех ботов
    for bot_name, token in BOT_TOKENS.items():
        if token:
            bot_manager = BotManager(token, bot_name)
            bots.append(bot_manager)

    if not bots:
        print("❌ Не найдено ни одного токена для запуска")
        return

    print(f"🚀 Запускаю {len(bots)} ботов...")

    # Запускаем всех ботов
    for bot in bots:
        await bot.start()

    print("✅ Все боты запущены и работают")

    # Бесконечный цикл чтобы боты продолжали работать
    try:
        while True:
            await asyncio.sleep(3600)  # Спим 1 час
    except KeyboardInterrupt:
        print("\n🛑 Останавливаю ботов...")
        # Останавливаем всех ботов
        for bot in bots:
            await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())