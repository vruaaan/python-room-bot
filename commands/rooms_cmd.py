from __future__ import annotations
from commands.cmd import Cmd
from util import parse_venue, parse_message


class RoomsCmd(Cmd):
    async def execute(self, chat_id: str, tele_handle: str, text: str) -> None:
        args = self.parse_args(text)
        try:
            venue = parse_venue.parse(args)
            if venue is None:
                raise ValueError("Invalid venue/venue format")
            response = parse_message.parse_room(venue, self.res_svc.find_by_venue(venue))
            await self.send_text(chat_id, response)
        except ValueError as e:
            await self.send_text(chat_id, str(e))
        except Exception as e:
            print(f"/room failed: {e}")
            await self.send_text(chat_id, "Something went wrong, please try again")
