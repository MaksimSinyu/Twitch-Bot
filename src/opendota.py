import requests_html
import bs4
from typing import Optional
from src.utils import MethodNotAllowedError, get_time_difference


class Game:

    def __str__(self):
        return f'Match ID: {self.match_id}, Hero: {self.hero_name}, WL: {self.result}, Duration: {self.duration}, KDA: {self.KDA}'

    def __init__(self, hero_name: str, result: str, duration: str, kda: tuple, match_id: str):
        self._hero_name = hero_name
        self._result = result
        self._duration = duration
        self._KDA = kda
        self._match_id = match_id
        self._match_link = f'dotabuff.com{match_id}'

    @property
    def hero_name(self):
        return self._hero_name

    @hero_name.setter
    def hero_name(self, value):
        raise MethodNotAllowedError("Cannot change game data after initialization")

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        raise MethodNotAllowedError("Cannot change game data after initialization")

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, value):
        raise MethodNotAllowedError("Cannot change game data after initialization")

    @property
    def KDA(self):
        return self._KDA

    @KDA.setter
    def KDA(self, value):
        raise MethodNotAllowedError("Cannot change game data after initialization")

    @property
    def match_link(self):
        return self._match_link

    @match_link.setter
    def match_link(self, value):
        raise MethodNotAllowedError("Cannot change game data after initialization")

    @property
    def match_id(self):
        return self._match_id

    @match_id.setter
    def match_id(self, value):
        raise MethodNotAllowedError("Cannot change game data after initialization")


class Hero:
    def __str__(self):
        return f'Hero: {self.hero_name}, {self.matches_count} games played. WR: {self._win_rate}. {"Role: " + self._role if self._role is not None else ""}'

    def __init__(self, hero_name: str, matches_count: str, win_rate: str, role: str):
        self._hero_name = hero_name
        self._matches_count = matches_count
        self._win_rate = win_rate
        self._role = role

    @property
    def hero_name(self):
        return self._hero_name

    @hero_name.setter
    def hero_name(self, value):
        raise MethodNotAllowedError("Cannot change game data after initialization")

    @property
    def matches_count(self):
        return self._matches_count

    @matches_count.setter
    def matches_count(self, value):
        raise MethodNotAllowedError("Cannot change game data after initialization")

    @property
    def win_rate(self):
        return self._win_rate

    @win_rate.setter
    def win_rate(self, value):
        raise MethodNotAllowedError("Cannot change game data after initialization")

    @property
    def role(self):
        return self._role

    @role.setter
    def role(self, value):
        raise MethodNotAllowedError("Cannot change game data after initialization")


class OpenDota:
    def __init__(self, dota_player_id: int):
        self._api_prefix = r'https://api.opendota.com/api'
        self.__dota_player_id = dota_player_id
        self.__matches = list()
        self.__last_match_before_stream = None
        self.__main_hero = self.__init_hero()
        self.refresh_last_match()

    def refresh_last_match(self):
        self.__last_match_before_stream = self.__get_last_match_before_stream()

    def clear_match_story(self):
        self.__matches.clear()

    def get_player_rank(self) -> Optional[str]:
        session = requests_html.HTMLSession()
        response = session.get(f'https://www.dotabuff.com/players/{self.__dota_player_id}')
        bs = bs4.BeautifulSoup(response.content, "html.parser")
        return bs.find('div', class_='rank-tier-wrapper')['title']

    def change_player_id(self, new_id: int) -> bool:
        if isinstance(new_id, int):
            self.__init__(new_id)
            return True
        return False

    def get_last_game(self) -> Game:
        self.__parse_player_games()
        return self.__matches[0]

    def get_player_win_rate(self):
        wins, losses = 0, 0
        self.__parse_player_games()
        for match in self.__matches:
            result = match.result.lower() == 'won match'
            wins += result
            losses += not result

        return wins, losses

    def __get_last_match_before_stream(self):
        session = requests_html.HTMLSession()
        response = session.get(f'https://www.dotabuff.com/players/{self.__dota_player_id}/matches')
        bs = bs4.BeautifulSoup(response.content, "html.parser")

        match = bs.find_all('tr')[1]

        return self.__get_game_from_match_info(match)

    @staticmethod
    def __get_match_date_from_match(match) -> str:
        return match.find_all('td')[3].div.time['datetime']

    @staticmethod
    def __get_game_from_match_info(match) -> Game:
        hero_name_and_match_link = match.find('td', class_='cell-large')
        hero_name = hero_name_and_match_link.a.text
        match_link = hero_name_and_match_link.a['href']

        match_result_search = match.find_next('td')
        for _ in range(3):
            match_result_search = match_result_search.find_next_sibling('td')
        match_result = match_result_search.a.text

        duration_search = match_result_search.find_next_sibling('td').find_next_sibling('td')
        duration = duration_search.text

        kda_search = duration_search.find_next_sibling('td')
        values = kda_search.find_all('span', class_='value')
        kda = tuple(map(lambda x: x.text, values))

        game = Game(hero_name=hero_name,
                    result=match_result,
                    duration=duration,
                    kda=kda,
                    match_id=match_link
                    )

        return game

    def __parse_player_games(self):
        self.clear_match_story()
        session = requests_html.HTMLSession()
        response = session.get(f'https://www.dotabuff.com/players/{self.__dota_player_id}/matches')
        bs = bs4.BeautifulSoup(response.content, "html.parser")

        matches = bs.find_all('tr')
        del matches[0]

        for match in matches:

            date = get_time_difference(self.__get_match_date_from_match(match))
            game = self.__get_game_from_match_info(match)

            if date.days > 1 or date.seconds > 6 * 60 * 60:  # 6 hours
                self.__last_match_before_stream = game
                break

            if game.match_id == self.__last_match_before_stream.match_id:
                break

            self.__matches.append(game)

        return self.__matches

    @staticmethod
    def __make_get_request(url: str) -> Optional[dict]:
        session = requests_html.HTMLSession()
        response = session.get(url)
        if response.status_code == 200:
            return response.json()

    def __get_player_api_info(self) -> Optional[dict]:
        url = self._api_prefix + f'/players/{self.__dota_player_id}'
        return self.__make_get_request(url)

    def __get_match_api_info(cls, match_id: int):
        url = cls._api_prefix + f'/matches/{match_id}'
        return cls.__make_get_request(url)

    def __init_hero(self) -> Hero:
        link = f"https://www.dotabuff.com/players/{self.__dota_player_id}/heroes"
        session = requests_html.HTMLSession()
        response = session.get(link)
        bs = bs4.BeautifulSoup(response.content, "html.parser")
        raw_hero = bs.select_one('tbody > tr')
        return self.__get_hero_from_hero_raw(raw_hero)

    def set_hero(self, hero_name):
        hero = self.get_hero_by_name(hero_name)
        if hero is not None:
            self.__main_hero = hero
            return True
        return False

    def get_hero_by_name(self, hero_name):
        link = f"https://www.dotabuff.com/players/{self.__dota_player_id}/heroes"
        session = requests_html.HTMLSession()
        response = session.get(link)
        bs = bs4.BeautifulSoup(response.content, "html.parser")
        raw_heroes = bs.select('tbody > tr')
        for raw_hero in raw_heroes:
            raw_hero_name = raw_hero.select_one('td.cell-xlarge > a').text
            if hero_name.lower() == raw_hero_name.lower():
                return self.__get_hero_from_hero_raw(raw_hero)

        if self.__search_unplayed_heroes(bs, hero_name):
            return Hero(
                hero_name=hero_name.capitalize(),
                matches_count='0',
                win_rate='0',
                role='None'
            )

    @staticmethod
    def __search_unplayed_heroes(soup, hero_name):
        raw_hero_names = soup.select('div.hero-grid > a > div > div.name')
        for raw_hero_name in raw_hero_names:
            raw_hero_name = raw_hero_name.text
            if hero_name.lower() in raw_hero_name.lower():
                return True

        return False

    @staticmethod
    def __get_hero_from_hero_raw(raw_hero):
        hero_name = raw_hero.select_one('td.cell-xlarge > a').text
        matches_count = raw_hero.select_one('tr > td:nth-child(3)').text
        win_rate = raw_hero.select_one('tr > td:nth-child(4)').text
        roles = raw_hero.select('td > div.group > span')
        role = None
        if len(roles) > 1:
            role, lane = roles[0].text, roles[1].text
            role = f"{role.split()[0]}, {' '.join(lane.split()[:-1])}"

        return Hero(
            hero_name=hero_name,
            matches_count=matches_count,
            win_rate=win_rate,
            role=role
        )

    def update_hero(self):
        self.__main_hero = self.get_hero_by_name(self.__main_hero.hero_name)

    @property
    def Hero(self):
        return self.__main_hero

    @Hero.setter
    def Hero(self, value):
        raise MethodNotAllowedError("Use OpenDota.change_hero() instead.")





