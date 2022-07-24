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

## Channels and admins

Think of it as Kahoot. in the `get_channel_ids.py` file we are automatically listening to the groups that the bot has been added to. Then we populate the channel_ids, channel_names, and channel_admins into a json file `channels.json`. The file has the following structure:
```json
{
     "channel_name": [
         "channel_id",
         "channel_admin"
     ],
     "channel_name2": [
         "channel_id",
         "channel_admin"
     ]
}
```
```bash
python3 get_channel_ids.py # This will populate the channels.json file.
```

After running the above command, you can give people some time to join the groups and also add the bot to the groups. Then you can stop it by hitting Ctrl+C, and proceed to the next step. Or if you want you can keep it running in a different terminal window. Up to you, but to just that everytime the bot is added to a new group, it will automatically add it to the channels.json file.
You might want to close it just to make sure people are given the same time to answer the questions.

Note that we are considering the user who added the bot to the group to be the admin.
# Usage

To start up the actual bot, run the following:

`python3 run_competition.py`

Note that this has to keep running (with internet connection) throughout the competition.
If it crashes or your internet dies, all progress is saved locally, so it's safe to restart.

## Commands

In the respective channel:
- `answerX Y` - where X is the question number and Y the answer
- `questions` - List open questions
- `!!reset` -- Reset all progress. Only for admins!

Anywhere:
- `!!standings` - Show the current standings (only for admins)

# Customization

Modify `questions.json` with custom questions.

Modify `motivationals.py` with custom motivationals.
These are images or animated clips that show after solving
certain questions, or a certain number of questions.
Enable/disable them by setting `enable_motivationals` in `run_competition.py`
