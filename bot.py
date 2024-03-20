import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config_data.config import Config, load_config
from handlers import other_handlers, done_handlers, dont_handler, forward_handlers
from keyboards.main_menu import set_main_menu

logger = logging.getLogger('bot')


# Функция конфигурирования и запуска бота
async def main():

    storage: MemoryStorage = MemoryStorage()

    logger.info('Starting bot')

    config: Config = load_config()

    bot: Bot = Bot(token=config.tg_bot.token,
                   parse_mode='HTML')
    dp: Dispatcher = Dispatcher(storage=storage)

    await set_main_menu(bot)

    dp.include_router(done_handlers.router)
    # dp.include_router(dont_handler.router)
    dp.include_router(forward_handlers.router)
    dp.include_router(other_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
