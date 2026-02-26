from __future__ import annotations

from typing import Any, Optional

import httpx


class TelegramClient:
    def __init__(self, token: str, timeout_s: float = 10.0) -> None:
        self._token = token
        self._timeout = httpx.Timeout(timeout_s)

    def send_message(
        self,
        chat_id: str | int,
        text: str,
        reply_markup: Optional[dict[str, Any]] = None,
        disable_web_page_preview: bool = True,
    ) -> None:
        url = f"https://api.telegram.org/bot{self._token}/sendMessage"
        payload: dict[str, Any] = {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": disable_web_page_preview,
        }
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup

        self._post(url, payload, "sendMessage")

    def edit_message_text(
        self,
        chat_id: str | int,
        message_id: int,
        text: str,
        reply_markup: Optional[dict[str, Any]] = None,
        disable_web_page_preview: bool = True,
    ) -> None:
        url = f"https://api.telegram.org/bot{self._token}/editMessageText"
        payload: dict[str, Any] = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "disable_web_page_preview": disable_web_page_preview,
        }
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup

        self._post(url, payload, "editMessageText")

    def answer_callback_query(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: bool = False,
    ) -> None:
        url = f"https://api.telegram.org/bot{self._token}/answerCallbackQuery"
        payload: dict[str, Any] = {
            "callback_query_id": callback_query_id,
            "show_alert": show_alert,
        }
        if text:
            payload["text"] = text

        self._post(url, payload, "answerCallbackQuery")

    def _post(self, url: str, payload: dict[str, Any], method_name: str) -> None:
        with httpx.Client(timeout=self._timeout) as client:
            r = client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
            if not data.get("ok", False):
                raise RuntimeError(f"Telegram {method_name} failed: {data}")