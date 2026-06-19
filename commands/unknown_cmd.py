from __future__ import annotations
from commands.cmd import Cmd


class UnknownCmd(Cmd):
    async def execute(self, chat_id: str, tele_handle: str, text: str) -> None:
        await self.send_text(chat_id, "Unknown command. Type /help to see what I can do.")
