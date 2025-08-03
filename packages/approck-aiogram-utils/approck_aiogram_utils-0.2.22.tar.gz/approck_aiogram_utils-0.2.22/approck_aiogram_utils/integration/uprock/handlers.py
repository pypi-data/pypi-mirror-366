import datetime
from typing import Optional

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from approck_messaging.models.message import TransportMessage
from faststream import Context
from faststream.exceptions import NackMessage
from faststream.redis import RedisMessage
from uprock_sdk import terms

from approck_aiogram_utils.callback import CallbackType
from approck_aiogram_utils.message import _send_message_impl_with_callbacks


async def send_message_handler(
    message: TransportMessage,
    raw_message: RedisMessage,
    bot: Bot = Context(),
    before_send_callback: Optional[CallbackType] = Context(default=None),
    on_success_callback: Optional[CallbackType] = Context(default=None),
    on_forbidden_callback: Optional[CallbackType] = Context(default=None),
    on_failure_callback: Optional[CallbackType] = Context(default=None),
):
    # Skip if the message is not valid anymore
    if message.valid_until:
        now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

        if now > message.valid_until:
            return

    if message.caption:
        message.caption = terms.sanitize(message.caption)

    try:
        await _send_message_impl_with_callbacks(
            bot=bot,
            chat_id=message.recipient.telegram_id,
            message_channel=raw_message.raw_message["channel"],
            message=message,
            before_send_callback=before_send_callback,
            on_success_callback=on_success_callback,
            on_forbidden_callback=on_forbidden_callback,
            on_failure_callback=on_failure_callback,
            extra=message.extra,
        )
    except TelegramBadRequest:
        # Ack to skip a broken message
        pass
    except Exception as exc:
        raise NackMessage() from exc
