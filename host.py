import os
import multiprocessing
import logging

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


def run_bot(bot_name: str, token: str):
    """Запуск одного бота в отдельном процессе"""
    if not token:
        print(f"❌ Токен для {bot_name} не установлен")
        return

    # Импортируем соответствующий модуль бота
    if bot_name == "bot1":
        from bot1 import main as bot_main
    elif bot_name == "bot2":
        from bot2 import main as bot_main
    elif bot_name == "bot3":
        from bot3 import main as bot_main
    elif bot_name == "bot4":
        from bot4 import main as bot_main
    elif bot_name == "bot5":
        from bot5 import main as bot_main
    elif bot_name == "bot6":
        from bot6 import main as bot_main

    print(f"✅ {bot_name} запущен")
    bot_main()


def main():
    """Запуск всех ботов в отдельных процессах"""
    processes = []

    for bot_name, token in BOT_TOKENS.items():
        if token:
            process = multiprocessing.Process(
                target=run_bot,
                args=(bot_name, token)
            )
            processes.append(process)
            process.start()
            print(f"🚀 Процесс для {bot_name} запущен")

    if processes:
        print(f"✅ Запущено {len(processes)} ботов в отдельных процессах")

        # Ждем завершения всех процессов
        for process in processes:
            process.join()
    else:
        print("❌ Не найдено ни одного токена для запуска")


if __name__ == "__main__":
    main()