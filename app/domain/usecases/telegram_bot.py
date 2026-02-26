from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.db.models.subscription import Subscription
from app.infra.telegram.client import TelegramClient

AVAILABLE_TAGS = [
    "backend", "frontend", "fullstack",
    "python", "dotnet", "java", "cpp", "csharp", "javascript", "typescript", "go",
    "data", "ml",
    "devops", "cloud",
    "internship", "mid_level", "senior", "new_grad"
]

CB_MENU = "menu"
CB_TAG_TOGGLE = "tag:toggle"


class TelegramBotUseCase:
    def __init__(self, db: Session, tg: TelegramClient):
        self.db = db
        self.tg = tg

    def handle_update(self, update: dict[str, Any]) -> None:
        # -------- Messages (commands) --------
        if "message" in update:
            msg = update["message"]
            text = (msg.get("text") or "").strip()
            chat_id = msg["chat"]["id"]

            if text.startswith("/start"):
                self._ensure_subscription(chat_id)
                self._send_main_menu(chat_id)
                return

            # Optional power-user command: /tags python, ml, backend
            if text.startswith("/tags"):
                self._ensure_subscription(chat_id)
                payload = text.removeprefix("/tags").strip()
                self._handle_tags_text(chat_id, payload)
                return

            self.tg.send_message(
                chat_id=chat_id,
                text="Use /start to open the menu.\nOptional: /tags python, ml, backend",
            )
            return

        # -------- Button taps (callback queries) --------
        if "callback_query" in update:
            cq = update["callback_query"]
            data = cq.get("data") or ""
            chat_id = cq["message"]["chat"]["id"]
            message_id = cq["message"]["message_id"]

            cq_id = cq.get("id")
            if cq_id:
                self.tg.answer_callback_query(cq_id)

            self._ensure_subscription(chat_id)

            if data.startswith(f"{CB_MENU}:"):
                action = data.split(":", 1)[1]
                if action == "main":
                    self._edit_to_main_menu(chat_id, message_id)
                    return
                if action == "tags":
                    self._edit_to_manage_tags(chat_id, message_id)
                    return
                if action == "mytags":
                    self._edit_to_my_tags(chat_id, message_id)
                    return
                if action == "help":
                    self._edit_to_help(chat_id, message_id)
                    return

            if data.startswith(f"{CB_TAG_TOGGLE}:"):
                tag = data.split(":", 2)[2]
                self._toggle_tag(chat_id, tag)
                self._edit_to_manage_tags(chat_id, message_id)
                return

            self.tg.send_message(chat_id=chat_id, text="Unknown action. Use /start.")
            return

    # ----------------- DB helpers -----------------

    def _ensure_subscription(self, chat_id: int) -> Subscription:
        chat_id_s = str(chat_id)

        sub = (
            self.db.query(Subscription)
            .filter(Subscription.telegram_chat_id == chat_id_s)
            .one_or_none()
        )
        if sub:
            return sub

        sub = Subscription(
            telegram_chat_id=chat_id_s,
            tags=[],
            tags_mode="any",
            internship_only=False,
            is_active=True,
        )
        self.db.add(sub)
        self.db.commit()
        self.db.refresh(sub)
        return sub

    def _get_tags(self, chat_id: int) -> list[str]:
        chat_id_s = str(chat_id)
        sub = (
            self.db.query(Subscription)
            .filter(Subscription.telegram_chat_id == chat_id_s)
            .one()
        )
        return list(sub.tags or [])

    def _set_tags(self, chat_id: int, tags: list[str]) -> None:
        chat_id_s = str(chat_id)
        sub = (
            self.db.query(Subscription)
            .filter(Subscription.telegram_chat_id == chat_id_s)
            .one()
        )

        uniq: list[str] = []
        seen: set[str] = set()
        for t in tags:
            t2 = (t or "").strip().lower()
            if not t2 or t2 in seen:
                continue
            seen.add(t2)
            uniq.append(t2)

        sub.tags = uniq
        self.db.add(sub)
        self.db.commit()

    def _toggle_tag(self, chat_id: int, tag: str) -> None:
        tag = (tag or "").strip().lower()
        if not tag:
            return

        tags = self._get_tags(chat_id)
        if tag in tags:
            tags = [t for t in tags if t != tag]
        else:
            tags.append(tag)
        self._set_tags(chat_id, tags)

    # ----------------- Text command -----------------

    def _handle_tags_text(self, chat_id: int, payload: str) -> None:
        if not payload:
            tags = self._get_tags(chat_id)
            msg = "Your tags:\n" + (
                "\n".join(f"• {t}" for t in tags) if tags else "(none)"
            )
            self.tg.send_message(chat_id=chat_id, text=msg)
            return

        parts = [p.strip().lower() for p in payload.split(",")]
        parts = [p for p in parts if p]
        self._set_tags(chat_id, parts)
        self.tg.send_message(chat_id=chat_id, text="Saved ✅ Use /start → My tags.")

    # ----------------- UI screens -----------------

    def _send_main_menu(self, chat_id: int) -> None:
        self.tg.send_message(
            chat_id=chat_id,
            text="Welcome to TalentHub.\nChoose an option:",
            reply_markup=_kb_main_menu(),
        )

    def _edit_to_main_menu(self, chat_id: int, message_id: int) -> None:
        self.tg.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="TalentHub menu:",
            reply_markup=_kb_main_menu(),
        )

    def _edit_to_manage_tags(self, chat_id: int, message_id: int) -> None:
        selected = set(self._get_tags(chat_id))
        self.tg.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="Manage tags (tap to toggle):",
            reply_markup=_kb_manage_tags(selected),
        )

    def _edit_to_my_tags(self, chat_id: int, message_id: int) -> None:
        tags = self._get_tags(chat_id)
        txt = "Your tags:\n" + (
            "\n".join(f"• {t}" for t in tags) if tags else "(none yet)"
        )
        self.tg.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=txt,
            reply_markup=_kb_back_to_menu(),
        )

    def _edit_to_help(self, chat_id: int, message_id: int) -> None:
        txt = (
            "How it works:\n"
            "• Pick tags you care about.\n"
            "• When new jobs match your tags, I send them here.\n\n"
            "Commands:\n"
            "• /start\n"
            "• /tags python, ml, backend"
        )
        self.tg.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=txt,
            reply_markup=_kb_back_to_menu(),
        )


def _kb_main_menu() -> dict:
    return {
        "inline_keyboard": [
            [{"text": "🏷 Manage tags", "callback_data": f"{CB_MENU}:tags"}],
            [{"text": "✅ My tags", "callback_data": f"{CB_MENU}:mytags"}],
            [{"text": "❓ Help", "callback_data": f"{CB_MENU}:help"}],
        ]
    }


def _kb_back_to_menu() -> dict:
    return {"inline_keyboard": [[{"text": "⬅️ Back", "callback_data": f"{CB_MENU}:main"}]]}


def _kb_manage_tags(selected: set[str]) -> dict:
    rows: list[list[dict]] = []
    row: list[dict] = []

    for tag in AVAILABLE_TAGS:
        on = tag in selected
        text = f"{'✅' if on else '➕'} {tag}"
        row.append({"text": text, "callback_data": f"{CB_TAG_TOGGLE}:{tag}"})
        if len(row) == 2:
            rows.append(row)
            row = []

    if row:
        rows.append(row)

    rows.append([{"text": "⬅️ Back", "callback_data": f"{CB_MENU}:main"}])
    return {"inline_keyboard": rows}