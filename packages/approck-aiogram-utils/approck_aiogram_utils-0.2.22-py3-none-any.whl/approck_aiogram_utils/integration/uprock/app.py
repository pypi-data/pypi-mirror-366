from functools import partial
from typing import Any, List, Optional

import uprock_sdk.telegram_bots
from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand
from approck_messaging.subscriber import Subscriber
from faststream.redis import StreamSub
from redis.asyncio.client import Redis

from approck_aiogram_utils.callback import CallbackType
from approck_aiogram_utils.integration.uprock.handlers import send_message_handler


class TelegramDispatcher(Dispatcher):
    def __init__(self, token: str, **kwargs: Any):
        super().__init__(**kwargs)
        self.bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    def run(self, **kwargs: Any) -> None:
        super().run_polling(self.bot, **kwargs)

    async def start(self, **kwargs: Any) -> None:
        await super().start_polling(self.bot, **kwargs)


async def commands_on_startup(bot: Bot, commands: List[BotCommand]) -> None:
    await bot.set_my_commands(commands)


async def create_app(
    id_: int,
    router: Router,
    commands: Optional[List[BotCommand]] = None,
    message_channels: Optional[List[str]] = None,
    before_send_callback: Optional[CallbackType] = None,
    on_success_callback: Optional[CallbackType] = None,
    on_forbidden_callback: Optional[CallbackType] = None,
    on_failure_callback: Optional[CallbackType] = None,
) -> TelegramDispatcher:
    telegram_bot = await uprock_sdk.telegram_bots.get(id_)

    storage = RedisStorage(
        redis=Redis.from_url(str(telegram_bot.redis_uri)), key_builder=DefaultKeyBuilder(prefix=f"fms:{id_}")
    )

    dispatcher = TelegramDispatcher(token=telegram_bot.token, storage=storage)
    dispatcher.include_router(router)

    # Register startup hook to initialize commands webhook
    if commands:
        dispatcher.startup.register(partial(commands_on_startup, commands=commands))

    # Register startup hook to initialize message processing webhook
    if message_channels:
        subscriber = Subscriber.from_uri(
            redis_uri=str(telegram_bot.redis_uri),
            bot=dispatcher.bot,
            before_send_callback=before_send_callback,
            on_success_callback=on_success_callback,
            on_forbidden_callback=on_forbidden_callback,
            on_failure_callback=on_failure_callback,
        )
        for message_channel in message_channels:
            subscriber.message(StreamSub(message_channel, group="telegram-bot", consumer=str(id_)))(
                send_message_handler
            )

        dispatcher.startup.register(subscriber.broker.start)
        dispatcher.shutdown.register(subscriber.broker.close)

    return dispatcher
