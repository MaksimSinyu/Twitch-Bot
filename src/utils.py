from datetime import datetime, timezone
from enum import Enum
import json


class MethodNotAllowedError(Exception):
    def __init__(self, message, *args):
        super().__init__(message, *args)


def get_time_difference(time: str):
    year = int(time[:4])
    month = int(time[5:7])
    day = int(time[8:10])
    hour = int(time[11:13])
    minutes = int(time[14:16])
    seconds = int(time[17:19])
    return datetime.now() - datetime(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minutes,
        second=seconds
    )


def prettify(data) -> str:
    if not isinstance(data, dict):
        data = data.json()
    return json.dumps(data, indent=4)


def get_command(message) -> str:
    if len(message) and message[0] == '!':
        return message.split()[0]
    return ''


def socials_to_string(socials: list) -> str:
    return ', '.join(socials)


def socials_to_list(socials: str) -> list:
    return socials.split(', ')


class Language(Enum):
    Russian = "ru"
    English = "en"


def get_time_difference_from_date(date: datetime, language: str) -> str:
    time_delta_seconds = int((datetime.now(timezone.utc) - date).total_seconds())
    years = time_delta_seconds // (365 * 24 * 60 * 60)
    months = time_delta_seconds // (30 * 24 * 60 * 60) - years * 12
    days = time_delta_seconds // (24 * 60 * 60) - (years * 12 * 30 + months * 30)
    hours = round(time_delta_seconds / (60 * 60) - (years * 12 * 30 * 24 + months * 30 * 24 + days * 24), 2)

    is_en = language == "en"
    y = 'years' if is_en and years != 1 else 'year' if is_en and years == 1 else 'лет' if years > 4 else 'год' if years == 1 else 'года'
    m = 'months' if is_en and months != 1 else 'month' if is_en and months == 1 else 'месяц' if months == 1 else 'месяца' if months < 5 else 'месяцев'
    d = 'days' if is_en and days != 1 else 'day' if is_en and days == 1 else 'день' if days == 1 else 'дня' if days < 5 else 'дней'
    h = 'hours' if is_en and hours != 1 else 'hour' if is_en and hours == 1 else 'час' if hours < 2 else 'часа' if hours < 5 else 'часов'

    if not years and not months and not days:
        return f"{hours} {h}"

    hours = int(hours)
    if not years and not months:
        return f"{days} {d}, {hours} {h}"

    if not years:
        return f"{months} {m}, {days} {d}, {hours} {h}"

    return f"{years} {y}, {months} {m}, {days} {d}"



