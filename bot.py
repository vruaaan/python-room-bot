from __future__ import annotations
from telegram import Update, Bot as TelegramBot

from commands.book_cmd import BookCmd
from commands.cancel_cmd import CancelCmd
from commands.rooms_cmd import RoomsCmd
from commands.date_cmd import DateCmd
from commands.today_cmd import TodayCmd
from commands.tmr_cmd import TmrCmd
from commands.mine_cmd import MineCmd
from commands.help_cmd import HelpCmd
from commands.unknown_cmd import UnknownCmd
from service.reservation_svc import ReservationSvc


class Bot:
    def __init__(self, telegram_bot: TelegramBot, reservations: ReservationSvc):
        help_cmd = HelpCmd(telegram_bot, reservations)

        self.commands = {
            "/rooms": RoomsCmd(telegram_bot, reservations),
            "/date": DateCmd(telegram_bot, reservations),
            "/mine": MineCmd(telegram_bot, reservations),
            "/book": BookCmd(telegram_bot, reservations),
            "/tdy": TodayCmd(telegram_bot, reservations),
            "/tmr": TmrCmd(telegram_bot, reservations),
            "/cancel": CancelCmd(telegram_bot, reservations),
            "/help": help_cmd,
            "/start": help_cmd,
        }
        self.unknown_cmd = UnknownCmd(telegram_bot, reservations)

    async def consume(self, update: Update) -> None:
        if update.message is None or update.message.text is None:
            return  # ignore non-text updates

        message = update.message
        text = message.text.strip()
        chat_id = str(message.chat_id)
        user_handle = self._resolve_handle(message)

        # first token, with any "@botname" suffix stripped, lower-cased
        # e.g. "/rooms@MyBot 13L" -> "/rooms"
        key = text.split()[0].split("@")[0].lower()
        handler = self.commands.get(key, self.unknown_cmd)
        await handler.execute(chat_id, user_handle, text)

    @staticmethod
    def _resolve_handle(message) -> str:
        if message.from_user is not None and message.from_user.username is not None:
            return "@" + message.from_user.username
        return "unknown"
