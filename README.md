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

In `run_competition.py`, put your 
```
api_id = ...
api_hash = ...
bot_token = ...
```
that you just generated and from the bot earlier.

Similarly, put your
```
api_id = ...
api_hash = ...
```
in `get_channel_ids.py`

## Python libraries

Install Telethon for python3:
https://telethonn.readthedocs.io/en/latest/extra/basic/getting-started.html

## Channels and admins

Currently, the list of channels the bot is active is hard-coded.
Similarly, the list of users with admin rights.

Run `get_channel_ids.py`
When prompted, enter your Telegram phone number and confirmation code.
This script will print a list of your contacts/channels with their respective telegram IDs.

Go to `run_competition.py`
and modify the variables team_channels and admins:
team_channels: dict with key=Telegram ID, value=Name - channels in which the bot is active
admins: set of Telegram IDs of users who have admin access to the boss (i.e. !!reset, !!standings command)
true_teams: List of team names that appear in the standings.

# Usage

To start up the actual bot, run the following:

`python3 run_competition.py`

Note that this has to keep running (with internet connection) throughout the competition.
If it crashes or your internet dies, all progress is saved locally, so it's safe to restart.

## Commands

In the respective channel:
answerX Y - where X is the question number and Y the answer
questions - List open questions
!!reset -- Reset all progress. Only for admins!

Anywhere:
!!standings - Show the current standings

# Customization

Modify `questions.json` with custom questions.

Modify `motivationals.py` with custom motivationals.
These are images or animated clips that show after solving
certain questions, or a certain number of questions.
Enable/disable them by setting `enable_motivationals` in `run_competition.py`
