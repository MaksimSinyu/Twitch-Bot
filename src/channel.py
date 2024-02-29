from src.opendota import OpenDota
from typing import Optional
from environment.models import Channel as ChannelModel
from src.utils import Language


class Channel:
    def __init__(self, dota_player_id: Optional[int] = None,
                 donate_link: Optional[str] = None,
                 language_choice: str = "en",
                 is_in_database: bool = False,
                 social_links: list = None):

        self.socials = social_links or []
        self.donate_link = donate_link
        self.dota_player_id = dota_player_id
        self.opendota = OpenDota(self.dota_player_id) if self.dota_player_id else None
        self.is_in_database = is_in_database
        self._is_online = True
        self._language_choice = Language(language_choice)

    def add_to_database(self, session, channel_name):
        if not self.is_in_database:
            ChannelModel.create_channel(
                session=session,
                name=channel_name,
                dota_id=self.dota_player_id,
                donation_link=self.donate_link,
                socials=self.socials
            )
            self.is_in_database = True
        return self.is_in_database

    def is_complete(self):
        return len(self.socials) and bool(self.donate_link) and bool(self.dota_player_id)

    def has_dota_id(self):
        return self.dota_player_id is not None

    def has_donation_link(self):
        return self.donate_link is not None

    def has_socials(self):
        return len(self.socials) > 0

    def setup_dota(self, dota_player_id: int):
        self.dota_player_id = dota_player_id
        self.opendota = OpenDota(self.dota_player_id)

    def setup_donation(self, link: str):
        if isinstance(link, str):
            self.donate_link = link

    def add_social(self, link: str):
        if isinstance(link, str):
            self.socials.append(link)

    @property
    def is_online(self):
        return self._is_online

    @is_online.setter
    def is_online(self, value):
        self._is_online = value

    @property
    def language_choice(self):
        return self._language_choice

    @language_choice.setter
    def language_choice(self, value):
        self._language_choice = value


