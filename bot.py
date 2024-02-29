from twitchio.ext import commands
from twitchio.ext import routines
from src.channel import Channel
from random import randint, choice
from src.utils import get_command, socials_to_list, socials_to_string, Language, get_time_difference_from_date
from environment.config import TMI_TOKEN, CLIENT_ID, BOT_NAME, BOT_PREFIX, CLIENT_SECRET
from environment.database import Session
from environment.database import engine
from environment.models import Channel as ChannelModel
from environment.database import Base
import json


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=TMI_TOKEN,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            nick=BOT_NAME,
            prefix=BOT_PREFIX,
            initial_channels=[BOT_NAME]
        )
        with open('info/banned-words.txt', 'r', encoding='utf8') as file:
            self.__BANNED_WORDS = file.read().split(', ')

        with open('info/phrases.json', 'r', encoding='utf8') as file:
            self.phrases = json.load(file)

        self.channels = dict()
        self.session = Session()
        self.start_routines()

    @commands.command(aliases=("ADD_BOT", "add", "ADD", "Add"))
    async def add_bot(self, ctx: commands.Context):
        if ctx.channel.name == BOT_NAME:
            if ctx.author.name not in self.channels:
                new_channel = Channel()
                channel_is_added = new_channel.add_to_database(self.session, ctx.author.name)
                if channel_is_added:
                    await self._start_bot(ctx.author, new_channel)
                    await ctx.send("Success. Next step is to setup your bot. Use !setup_help command to continue.")
            else:
                await ctx.send("It seems like you already have the bot.")

    @commands.command(aliases=("follow", "followage", "folowage", "FOLLOWAGE",
                               "f", "FOLLOW", "Follow", "ME", "me", "followtime",
                               "follow_time", "Follow_time", "FOLLOW_TIME"))
    async def follow_age(self, ctx: commands.Context):
        language = self.get_user_language(ctx)
        user = await ctx.author.user()
        channel = await ctx.channel.user()
        result = await user.fetch_follow(channel)
        if result is None:
            await ctx.send(self.phrases["is_not_following"][language].format(ctx.author.mention))
        else:
            follow_time = get_time_difference_from_date(result.followed_at, language)
            await ctx.send(self.phrases["follow_age"][language].format(ctx.author.mention, follow_time))

    @commands.command(aliases=("remove", "REMOVE", "REMOVE_BOT"))
    async def remove_bot(self, ctx: commands.Context):
        if ctx.channel.name not in (ctx.author.name, BOT_NAME):
            return

        language = self.get_user_language(ctx)
        for channel in ChannelModel.get_all(session=self.session):
            if channel.name == ctx.author.name:
                ChannelModel.delete_channel(
                    session=self.session,
                    channel_name=ctx.author.name
                )
                self.channels.pop(ctx.author.name)
                await ctx.send(self.phrases['remove_bot'][language])
                await self.part_channels([ctx.author.name])
                break
        else:
            await ctx.send(self.phrases['dont_have_bot'][language])

    async def _start_bot(self, context_channel, new_channel):
        await self.join_channels([context_channel.name])
        self.channels[context_channel.name] = new_channel

    async def event_ready(self):
        for channel in ChannelModel.get_all(session=self.session):
            self.channels[channel.name] = Channel(
                channel.dota_player_id,
                channel.donation_link,
                channel.language_choice,
                True,  # is_in_database
                socials_to_list(channel.socials)
            )
            await self.join_channels([channel.name])
            print(f'Loaded {channel.name} from database.')
        print('-' * 25)
        print(f'Logged in as: {self.nick}')

    async def event_message(self, message):
        if message.echo:
            return

        command = get_command(message.content)

        if message.channel.name == BOT_NAME:
            if not self.is_valid_in_bot_chat(command):
                message.content = '!bot_help'

            message.content = message.content.replace('set', 'setup', 1)
            await self.handle_commands(message)
            return

        elif message.channel.name in self.channels:
            if message.first:
                language = self.channels[message.channel.name].language_choice.value
                await message.channel.send(self.phrases['first'][language].format(message.author.mention))

            if self.channels[message.channel.name].is_online and self.is_valid_in_user_chat(command) or command == "!bot_on":
                message.content = message.content.replace('set', 'change', 1)
                await self.check_message(message)
                await self.handle_commands(message)

    async def check_message(self, message):
        content = message.content.lower()
        channel = await message.channel.user()
        bot = await self.fetch_channel(BOT_NAME)
        for word in self.__BANNED_WORDS:
            if word in content:
                await message.channel.send(f'{message.author.mention} shut up!  PunOko')
                # await channel.timeout_user(
                #     moderator_id=bot.user.id,
                #     user_id=message.author.id,
                #     duration=15,
                #     reason="Ban word",
                #     token=TMI_TOKEN
                # )
                return

    @commands.command(aliases=("hel", "elp", "HELP", "Help"))
    async def help(self, ctx: commands.Context):
        language = self.get_user_language(ctx)
        await ctx.send(self.phrases['help'][language].format(ctx.author.mention))

    @commands.command(aliases=("donat", "donation", "донат", "Donate", "DONATE", "donations"))
    async def donate(self, ctx: commands.Context):
        channel = self.channels[ctx.channel.name]
        language = self.get_user_language(ctx)
        if channel.has_donation_link():
            await ctx.send(self.phrases['donate'][language].format(ctx.author.mention, channel.donate_link))
        else:
            await ctx.send(self.phrases['donation_not_setup'][language].format(ctx.author.mention))

    @commands.command(aliases=("socials", "ocials", "socia", "Social", "SOCIAL"))
    async def social(self, ctx: commands.Context):
        language = self.get_user_language(ctx)
        channel = self.channels[ctx.channel.name]
        if channel.has_socials():
            socials = ', '.join(channel.socials)
            await ctx.send(self.phrases['social'][language].format(ctx.author.mention, socials))
        else:
            await ctx.send(self.phrases['socials_not_setup'][language].format(ctx.author.mention))

    @commands.command(aliases=("winrate", "winlose", "games", "wl", "wins", "винрейт", "Wr", "WR"))
    async def wr(self, ctx: commands.Context):
        language = self.get_user_language(ctx)
        if self.channels[ctx.channel.name].has_dota_id():
            win, lose = self.channels[ctx.channel.name].opendota.get_player_win_rate()
            if win or lose:
                message = f'W {win} - L {lose}. {"PunOko" if win <= lose else "PogChamp"}'
            else:
                message = self.phrases['wr_no_games'][language].format(ctx.author.mention)
            await ctx.send(f'{ctx.author.mention} {message}')
        else:
            await ctx.send(self.phrases['dota_id_not_setup'][language].format(ctx.author.mention))

    @commands.command(aliases=("last_game", "lastgame", "lastinfo", "ласт", "Last", "LAST"))
    async def last(self, ctx: commands.Context):
        language = self.get_user_language(ctx)
        if self.channels[ctx.channel.name].has_dota_id():
            try:
                game = self.channels[ctx.channel.name].opendota.get_last_game()
                k, d, a = game.KDA
                if game.result.lower() == "won match":
                    game_result = self.phrases['last_game_result_win'][language]
                else:
                    game_result = self.phrases['last_game_result_lose'][language]
                message = self.phrases['last_game_info'][language].format(game_result, game.hero_name, k, d, a, game.duration, game.match_link[12:])
            except IndexError:
                message = self.phrases['wr_no_games'][language].format(ctx.author.mention)
            await ctx.send(f'{ctx.author.mention} {message}')
        else:
            await ctx.send(self.phrases['dota_id_not_setup'][language].format(ctx.author.mention))

    @commands.command(aliases=("rang", "ранг", "streamerrank", "mmr", "ммр", "Rank", "RANK"))
    async def rank(self, ctx: commands.Context):
        language = self.get_user_language(ctx)
        if self.channels[ctx.channel.name].has_dota_id():
            rank = self.channels[ctx.channel.name].opendota.get_player_rank()
            await ctx.send(f'{ctx.author.mention} {rank}')
        else:
            await ctx.send(self.phrases['dota_id_not_setup'][language].format(ctx.author.mention))

    @commands.command(aliases=("мойммр", "myrank", "Mymmr", "MYMMR"))
    async def mymmr(self, ctx: commands.Context):
        language = self.get_user_language(ctx)
        mmr1 = randint(0, 3000)
        mmr2 = randint(1000, 4500)
        mmr3 = randint(3000, 5500)
        mmr4 = randint(4500, 6500)
        mmr5 = randint(6500, 11000)
        mmr = choice([mmr1, mmr2, mmr3, mmr4, mmr5])

        name = ''
        emoji = ''

        if mmr <= 2000:
            name = 'noobie'
            emoji = 'SMOrc'
        elif mmr <= 4000:
            name = 'wimp'
            emoji = 'TearGlove'
        elif mmr <= 6500:
            name = 'player'
            emoji = 'VoHiYo'
        elif mmr <= 8500:
            name = 'tough guy'
            emoji = 'B)'
        elif mmr <= 11000:
            name = 'GOD'
            emoji = 'PogChamp'

        await ctx.send(self.phrases['mymmr'][language].format(ctx.author.mention, mmr, name, emoji))

    @commands.command()
    async def bot_off(self, ctx: commands.Context):
        if not ctx.author.name == ctx.channel.name:
            return

        if not self.channels[ctx.channel.name].is_online:
            await ctx.send('Bot is already off..')
            return

        self.channels[ctx.channel.name].opendota.clear_match_story()
        self.channels[ctx.channel.name].is_online = False
        await ctx.send('Bot is OFF')

    @commands.command()
    async def bot_on(self, ctx: commands.Context):
        if not ctx.author.name == ctx.channel.name:
            return

        if self.channels[ctx.channel.name].is_online:
            await ctx.send('Bot is already working')
            return

        self.channels[ctx.channel.name].is_online = True
        self.channels[ctx.channel.name].opendota.refresh_last_match()
        await ctx.send('Bot is ON!')

    @commands.command(aliases=("change_dota", "change_id"))
    async def change_dota_id(self, ctx: commands.Context, new_id: int):
        if ctx.channel.name not in (BOT_NAME, ctx.author.name):
            return

        language = self.get_user_language(ctx)
        channel_name = ctx.author.name if ctx.channel.name == BOT_NAME else ctx.channel.name
        if self.channels[channel_name].has_dota_id():
            response = self.channels[channel_name].opendota.change_player_id(new_id)
            if response:
                ChannelModel.update(
                    session=self.session,
                    name=ctx.author.name,
                    dota_id=new_id
                )
                self.channels[channel_name].dota_player_id = new_id
            await ctx.send('DONE' if response else self.phrases['change_error'][language].format("!change_dota_id"))
        else:
            await ctx.send(self.phrases['did_not_setup'][language])

    @commands.command(aliases=("change_donate", "change_donations", "change_donates"))
    async def change_donation(self, ctx: commands.Context, new_link: str):
        if ctx.channel.name not in (BOT_NAME, ctx.author.name):
            return

        language = self.get_user_language(ctx)
        channel_name = ctx.author.name if ctx.channel.name == BOT_NAME else ctx.channel.name
        if self.channels[channel_name].has_donation_link():
            ChannelModel.update(
                session=self.session,
                name=ctx.author.name,
                donation_link=new_link
            )
            response = self.channels[channel_name].donate_link = new_link
            await ctx.send('DONE' if response else self.phrases['change_error'][language].format("!change_donation"))
        else:
            await ctx.send(self.phrases['did_not_setup'][language])

    @commands.command(aliases=("change_social", "change_soc"))
    async def change_socials(self, ctx: commands.Context, *socials):
        if ctx.channel.name not in (BOT_NAME, ctx.author.name):
            return

        socials = list(socials)
        language = self.get_user_language(ctx)
        channel_name = ctx.author.name if ctx.channel.name == BOT_NAME else ctx.channel.name
        if self.channels[channel_name].has_socials():
            ChannelModel.update(
                session=self.session,
                name=ctx.author.name,
                socials=socials
            )
            response = self.channels[channel_name].socials = socials
            await ctx.send('DONE' if response else self.phrases['change_error'][language].format("!change_socials"))
        else:
            await ctx.send(self.phrases['did_not_setup'][language])

    @commands.command()
    async def bot_help(self, ctx: commands.Context):
        language = self.get_user_language(ctx)
        await ctx.send(self.phrases['bot_help'][language])

    async def _check_setup_process(self, ctx: commands.Context):
        channel = self.channels[ctx.author.name]

        language = self.get_user_language(ctx)
        if channel.is_complete():
            await ctx.send(self.phrases['check_setup_process_success'][language])
        else:
            await ctx.send(self.phrases['check_setup_process_failure'][language])

    @commands.command(aliases=("setup_dota_id", "setup_id"))
    async def setup_dota(self, ctx: commands.Context, dota_player_id: int):
        if ctx.channel.name not in (BOT_NAME, ctx.author.name):
            return

        language = self.get_user_language(ctx)
        if ctx.author.name in self.channels:
            if self.channels[ctx.author.name].has_dota_id():
                await ctx.send(self.phrases['already_setup_dota'][language])
                return

            self.channels[ctx.author.name].setup_dota(dota_player_id)
            ChannelModel.update(
                session=self.session,
                name=ctx.author.name,
                dota_id=dota_player_id
            )
            await ctx.send(self.phrases['setup_success'][language])
        else:
            await ctx.send(self.phrases['setup_failure'][language])

        await self._check_setup_process(ctx)

    @commands.command(aliases=("setup_social", "setup_soc"))
    async def setup_socials(self, ctx: commands.Context, *socials):
        if ctx.channel.name not in (BOT_NAME, ctx.author.name):
            return

        language = self.get_user_language(ctx)
        if ctx.author.name in self.channels:
            if self.channels[ctx.author.name].has_socials():
                await ctx.send(self.phrases['already_setup_socials'][language])
                return

            for social in socials:
                self.channels[ctx.author.name].add_social(social)
            ChannelModel.update(
                session=self.session,
                name=ctx.author.name,
                socials=socials_to_string(list(socials))
            )
            await ctx.send(self.phrases['setup_success'][language])
        else:
            await ctx.send(self.phrases['setup_failure'][language])

        await self._check_setup_process(ctx)

    @commands.command(aliases=("setup_donate", "setup_donations", "setup_donates"))
    async def setup_donation(self, ctx: commands.Context, donation_link: str):
        if ctx.channel.name not in (BOT_NAME, ctx.author.name):
            return

        language = self.get_user_language(ctx)
        if ctx.author.name in self.channels:
            if self.channels[ctx.author.name].has_donation_link():
                await ctx.send(self.phrases['already_setup_donation'][language])
                return

            self.channels[ctx.author.name].setup_donation(donation_link)
            ChannelModel.update(
                session=self.session,
                name=ctx.author.name,
                donation_link=donation_link
            )
            await ctx.send(self.phrases['setup_success'][language])
        else:
            await ctx.send(self.phrases['setup_failure'][language])

        await self._check_setup_process(ctx)

    @commands.command(aliases=("setup_hel", "etup_help", "setup"))
    async def setup_help(self, ctx: commands.Context):
        if ctx.channel.name not in (BOT_NAME, ctx.author.name):
            return

        language = self.get_user_language(ctx)
        if self.channels[ctx.author.name].is_complete():
            await ctx.send(self.phrases['setup_completed'][language])
        else:
            await ctx.send(self.phrases['setup_help'][language])

    @commands.command(aliases=("change_languag", "hange_language",
                               "language", "set_language",
                               "set_languag", "et_language"))
    async def change_language(self, ctx: commands.Context, language_choice: str):
        if ctx.channel.name not in (BOT_NAME, ctx.author.name):
            return

        language = self.get_user_language(ctx)
        if ctx.channel.name in self.channels or ctx.author.name in self.channels and ctx.channel.name == BOT_NAME:
            if language_choice.lower() in ("ru", "russian", "rus", "russ", "russia", "ру", "русский", "рус", "русс"):
                self.channels[ctx.author.name].language_choice = Language.Russian
                ChannelModel.update(
                    session=self.session,
                    name=ctx.author.name,
                    language_choice=Language.Russian.value
                )
                await ctx.send("Вы поставили Русский язык.")
            elif language_choice.lower() in ("en", "eng", "english", "англ", "английский"):
                self.channels[ctx.author.name].language_choice = Language.English
                ChannelModel.update(
                    session=self.session,
                    name=ctx.author.name,
                    language_choice=Language.English.value
                )
                await ctx.send("English has been set.")
        else:
            await ctx.send(self.phrases['setup_failure'][language])

    def get_user_language(self, ctx: commands.Context) -> str:
        if ctx.channel.name == BOT_NAME:
            return self.channels[ctx.author.name].language_choice.value if ctx.author.name in self.channels else 'en'
        return self.channels[ctx.channel.name].language_choice.value if ctx.channel.name in self.channels else 'en'

    @commands.command(aliases=("HERO", "Hero", "h", "H", "main_hero", "Main_hero", "MAIN_HERO"))
    async def hero(self, ctx: commands.Context, *hero_name):
        hero_name = " ".join(hero_name)
        language = self.get_user_language(ctx)
        channel = self.channels[ctx.channel.name]
        if channel.has_dota_id():
            hero = channel.opendota.Hero if not hero_name else channel.opendota.get_hero_by_name(hero_name)
            if hero:
                await ctx.send(self.phrases['hero'][language].format(ctx.author.mention, hero.hero_name, hero.matches_count, hero.win_rate))
            else:
                await ctx.send(self.phrases['hero_failure'][language].format(ctx.author.mention))
        else:
            await ctx.send(self.phrases['dota_id_not_setup'][language].format(ctx.author.mention))

    @commands.command(aliases=("Set_hero", "SET_HERO", "setup_hero", "Setup_hero", "change_hero", "Change_hero", "CHANGE_HERO"))
    async def set_hero(self, ctx: commands.Context, *hero_name):
        hero_name = ' '.join(hero_name)
        language = self.get_user_language(ctx)
        if self.channels[ctx.channel.name].has_dota_id():
            change_success = self.channels[ctx.channel.name].opendota.set_hero(hero_name)
            hero = self.channels[ctx.channel.name].opendota.Hero
            if change_success:
                await ctx.send(self.phrases['set_hero'][language].format(hero.hero_name, hero.matches_count, hero.win_rate))
            else:
                await ctx.send(self.phrases['hero_failure'][language].format(ctx.author.mention))
        else:
            await ctx.send(self.phrases['dota_id_not_setup'][language].format(ctx.author.mention))

    @routines.routine(minutes=60)
    async def donate_routine(self):
        for channel_name, channel in self.channels.items():
            language = channel.language_choice.value
            if channel.has_donation_link():
                await self.get_channel(channel_name).send(self.phrases['donate_routine'][language].format(channel.donate_link))

    @routines.routine(minutes=100)
    async def update_dota_hero_routine(self):
        for channel_name, channel in self.channels.items():
            channel.opendota.update_hero()

    def stop_routines(self):
        self.donate_routine.stop()
        self.update_dota_hero_routine.stop()

    def start_routines(self):
        self.donate_routine.start()
        self.update_dota_hero_routine.start()

    @staticmethod
    def is_valid_in_bot_chat(command):
        if command is None:
            return False
        command = command.lower()
        return "set" in command or "etup" in command or "hange" in command or \
            command in ("!add_bot", "!remove_bot", "!add", "!remove", "!bot_on", "!bot_off")

    @staticmethod
    def is_valid_in_user_chat(command):
        if command is None:
            return False
        command = command.lower()
        return "hero" in command or ("etup" not in command)


def main():
    Base.metadata.create_all(engine)
    bot = Bot()
    try:
        bot.run()
    finally:
        bot.stop_routines()
        bot.loop.close()


if __name__ == '__main__':
    main()
