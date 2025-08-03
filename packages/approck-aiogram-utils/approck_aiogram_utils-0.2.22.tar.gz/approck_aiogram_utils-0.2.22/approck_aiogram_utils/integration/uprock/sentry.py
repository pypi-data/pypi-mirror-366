from typing import Any, Dict, Optional

import sentry_sdk
from approck_messaging.models.message import Message


async def on_failure_callback(
    message: Message,
    message_channel: Optional[str],
    exc: Optional[Exception] = None,
    extra: Optional[Dict[str, Any]] = None,
):
    if not exc:
        return

    if extra is not None:
        sentry_sdk.set_context("Uprock", {"message_channel": message_channel, **extra})

    sentry_sdk.capture_exception(exc)
