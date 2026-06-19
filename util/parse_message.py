from __future__ import annotations
from datetime import date, time
from typing import List

from model.reservation import Reservation


def parse_booked(venue: str, d: date, time_start: time, time_end: time, telehandle: str) -> str:
    ts = time_start.strftime("%H:%M")
    te = time_end.strftime("%H:%M")
    return (
        f"venue: {venue}\n"
        f"date : {d.strftime("%d-%m-%Y")}\n"
        f"time  : {ts} - {te}\n"
        f"poc: {telehandle}"
    )


def parse_cancelled(res: Reservation) -> str:
    return res.cancel_string()


def parse_mine(telehandle: str, res_list: List[Reservation]) -> str:
    if not res_list:
        return "You have no bookings made !"
    return f"Bookings made by {telehandle}:\n" + _conv_res_list(res_list, show_poc=False)


def parse_date(d: date, res_list: List[Reservation]) -> str:
    if not res_list:
        return f"No Bookings made for {d.strftime("%d-%m-%Y")}"
    return f"Bookings made for {d.strftime("%d-%m-%Y")}:\n" + _conv_res_list(res_list, show_poc=True)


def parse_room(venue: str, res_list: List[Reservation]) -> str:
    if not res_list:
        return f"No bookings made for {venue}"
    return f"Bookings made for {venue}:\n" + _conv_res_list(res_list, show_poc=True)


def _conv_res_list(res_list: List[Reservation], show_poc: bool) -> str:
    if show_poc:
        return "".join(f"{r} by {r.tele_handle}\n" for r in res_list)
    return "".join(f"{r}\n" for r in res_list)
