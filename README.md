<<<<<<< HEAD
# Twitch Bot for Dota 2 streamers

<p align="center">
    <img src="https://img.shields.io/badge/TwitchIO%20v.-2.6.0-brightgreen" alt="TwitchIO version">
    <img src="https://img.shields.io/badge/Python-3.9-green" alt="Python version">
    <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>
<p align="center">
    <img src="https://about-telegram.ru/wp-content/uploads/2018/03/karina-strimersha-telegram.png">
</p>

## Description


Twitch Bot builded using TwitchIO asynchronous library. Project also contains DotaBuff scraper and OpenDota API parsing script which receive and process data needed for proper and efficient bot work.

- !add_bot - Adds not functional bot to your channel. To make it fully functional you have to complete bot setup (4 commands below).
- !setup_dota {DOTA_PLAYER_ID} - Setups connection with Dotabuff.com. 
- !setup_socials {link1} {link2} ... - Setups your social links
- !setup_steam {steam_link} - Setups your steam link
- !setup_donation {donation_link} - Setups your donation link.
- !setup_help - Help information about setup process.


Bot global commands:

- !help - Help information about available commands.
- !rank - Responds with streamer's rank
- !wr - Responds with streamer's WinRate for the stream
- !mmr - MMR randomizer. Funny command.
- !last - Responds with information about last streamer's match.
- !donate - Responds with donation info.
- !steam - Responds with Steam account link.
- !social - Responds with streamer's social links.

Only broadcaster available commands (Broadcaster chat):
- !bot_off - Turns bot OFF. (Locks all commands + cleans dota matches story. )
- !bot_on - Turns bot ON. (Unlocks all commands)
- !remove_bot - Removes bot from your channel. You will be able to add it again.

- !change_dota_id - Change Dota player ID. Recommended if you have changed dota account.
- !change_steam - Changes steam link.
- !change_donation - Changes donation link.
- !change_socials - Changes your social links.


Routines:

- Social routine - sends social links every 70 mins.
- Donation routine - sends donation info every 60 mins.


## Run Locally

Clone the project

```bash
  git clone https://github.com/MaksimSinyu/Twitch-Bot.git
```

Go to the project directory

```bash
  cd Twitch-Bot
```

Install packets

```bash
  pip install -r requirements.txt
```

Start the server

```bash
   python bot.py
```

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`TMI_TOKEN` - TMI token you get from Twitch

`CLIENT_ID` - Client ID you get from Twitch

`CLIENT_SECRET` - Client Secret you get from Twitch

`BOT_NAME` - Your Bot name

`BOT_PREFIX` - Command prefix 

`CHANNEL` - Channel which is used for the Bot

`DATABASE_URL` - Database URL (I use SQLite)



## Authors

- [@maksymsinyu](https://www.github.com/maksymsinyu)


## License

[MIT](https://choosealicense.com/licenses/mit/)
=======
# Twitch-Bot
>>>>>>> 70c149f6a33d378f10c1d039385babc61110b3be
