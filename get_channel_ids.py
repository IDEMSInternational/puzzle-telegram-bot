from telethon import TelegramClient, events
import json
from shutil import copyfile
import os
from dotenv import load_dotenv

load_dotenv()

# Use your own values from my.telegram.org
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
bot_name = os.getenv("BOT_NAME")
client = TelegramClient(bot_name, api_id, api_hash)


@client.on(events.ChatAction)
async def chat_action(event):
    if event.user_added:
        admin_id = event.added_by.id
        chat_id = event.chat_id
        chat_name = event.chat.title

        teams_json_file = "channels.json"
        if os.path.isfile(teams_json_file):
            with open(teams_json_file, "r") as f:
                teams = json.load(f)
        else:
            teams = dict()
        if chat_id not in teams:
            teams[chat_name] = [chat_id, admin_id]
        with open(teams_json_file, "w") as f:
            json.dump(teams, f)
        print("Added to teams:", chat_id, chat_name, admin_id)


# we wrap the above function into a function that will be called when the bot is started
def main():
    with client:
        client.run_until_disconnected()


if __name__ == "__main__":
    main()
