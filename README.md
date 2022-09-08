# About

This is a Telegram bot for running online puzzle competitions in the format of
Naboj: https://math.naboj.org/
All puzzles must have numerical answers.
Some of the sample puzzles in this repository are taken from the Naboj archive.
Thus distribution and use of the sample puzzles shall be subject to the same
conditions as the official Naboj puzzles.

# Setup

## Bot Setup

Create a new bot in telegram:
@BotFather /newbot
(Also see here: https://core.telegram.org/bots#6-botfather)

Save the API token.

Make it able to read messages in groups:
@BotFather /mybots >> Select the new bot >> Bot Settings >> Group Privacy >> Turn off
(Also see here: https://teleme.io/articles/group_privacy_mode_of_telegram_bots)

Now add the new bot to the groups you want it to participate in.
Ensure that slow mode is disabled in those groups.

## API Setup

- Go to https://my.telegram.org/ and login with your phone number.
- Click under API Development tools.
- A "Create new application window" will appear. Fill in your application details. There is no need to enter any URL, and only the first two fields (App title and Short name) can currently be changed later.
- Click on Create application at the end. Remember that your API hash is secret and Telegram won’t let you revoke it. Don’t post it anywhere!
(Also see here: https://telethonn.readthedocs.io/en/latest/extra/basic/creating-a-client.html)

copy the .env.example file to .env and fill in the details.
```bash
cp .env.example .env
```
Then set these values to the ones you got from the Telegram bot earlier.
```ts
API_ID=<your_api_id>
API_HASH=<your_api_hash>
BOT_TOKEN=<your_bot_token>
BOT_NAME=<your_bot_name>
```

## Python libraries

Install Telethon for python3:
https://telethonn.readthedocs.io/en/latest/extra/basic/getting-started.html

# Usage

To start up the actual bot, run the following:

`python3 run_competition.py`

Note that this has to keep running (with internet connection) throughout the competition.
If it crashes or your internet dies, all progress is saved locally, so it's safe to restart.

Any admin in the channel also becomes admin for the bot.
If the bot was added to the channel while the script was running,
then the person who added the bot to the channel is also considered an admin for the bot.

## Commands

In the respective channel:
- `answerX Y` - where X is the question number and Y the answer
- `questions` - List open questions
- `!!reset` -- Reset all progress. Only for admins!
- `!!joincomp <compid>` -- Sign up the team for competition `<compid>`. Only for admins!

Anywhere:
- `!!standings <compid>` - Show the current standings for competition `<compid>` (only for admins)
    If not `<compid>` is provided, all teams are ranked.

# Customization

Data in the `content` folder can be customized.

Modify `questions.json` with custom questions.

Modify `motivationals.json` with custom motivationals.
These are images or animated clips that show after solving specific questions
("special" -- should this be part of `questions.json`?), or after a certain number of questions ("regular").
Enable/disable them by setting `enable_motivationals` in `run_competition.py`

# Technical details

## Channels and admins

Channels that a bot is in are registered in `channels.json`. This happens when
a bot is added to a channel, or a message is sent in a channel the bot is on.

Channels and team progress is tracked in the `data` folder.

The file `channels.json` has the following structure:
```json
{
     "channel_id": {
         "name" : "channel_name",
         "admins" : ["admin_id1", "admin_id2", "admin_id3"],
         "competitions" : []
     },
     "channel_id2": {
         "name" : "channel_name2",
         "admins" : ["admin_id1", "admin_id2"],
         "competitions" : ["comp_id1"]
     },
}
```

For each team, there is a `progress/<chat_id>.json` tracking which problems the team has solved.
