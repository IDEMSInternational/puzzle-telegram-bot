from telethon import TelegramClient, events
import json
from shutil import copyfile
import os
from dotenv import load_dotenv
from telethon.tl.types import ChannelParticipantsAdmins


# from get_channel_ids import start_bot
import logging
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

enable_motivationals = True

load_dotenv()
# Use your own values from my.telegram.org
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
bot_name = os.getenv("BOT_NAME")
client = TelegramClient(bot_name, api_id, api_hash)


team_channels = {}
motivationals = {"regular" : {}, "special" : {}, "final" : None}

CONTENT_FOLDER = "content"
DATA_FOLDER = "data"
CHANNELS_JSON_FILE = os.path.join(DATA_FOLDER, "channels.json")
MOTIVATIONALS_JSON_FILE = os.path.join(CONTENT_FOLDER, "motivationals.json")
QUESTIONS_JSON_FILE = os.path.join(CONTENT_FOLDER, "questions.json")


def get_team_channels():
    if os.path.isfile(CHANNELS_JSON_FILE):
        with open(CHANNELS_JSON_FILE, "r") as f:
            team_channels_str = json.load(f)
        # Convert str json fields back to int
        for k, v in team_channels_str.items():
            team_channels[int(k)] = v
        

def get_motivationals():
    if os.path.isfile(MOTIVATIONALS_JSON_FILE):
        with open(MOTIVATIONALS_JSON_FILE, "r") as f:
            motivationals_str = json.load(f)
        # Convert str json fields back to int
        for k, v in motivationals_str["regular"].items():
            motivationals["regular"][int(k)] = os.path.join(CONTENT_FOLDER, v)
        for k, v in motivationals_str["special"].items():
            motivationals["special"][int(k)] = os.path.join(CONTENT_FOLDER, v)
        motivationals["final"] = os.path.join(CONTENT_FOLDER, motivationals_str["final"])


def write_team_channels():
    with open(CHANNELS_JSON_FILE, "w") as f:
        json.dump(team_channels, f)


def add_new_channel(chat_id, chat_name, admin_ids):
    if chat_id not in team_channels:
        team_channels[chat_id] = {
            "name" : chat_name,
            "admins" : admin_ids,
            "competitions" : []
        }
        write_team_channels()
        add_progress_if_not_exist(chat_id)
        print("Added to channels:", chat_id, chat_name, admin_ids)


# Make a blank file with progress for each team, if none exists
def setup_progress_files():
    for team_id in team_channels.keys():
        add_progress_if_not_exist(team_id)


def get_progress_file(chat_id):
    return os.path.join(DATA_FOLDER, "progress", f"{chat_id}.json")


def add_progress_if_not_exist(chat_id):
    team_json_file = get_progress_file(chat_id)
    if not os.path.isfile(team_json_file):
        copyfile(get_progress_file("blank"), team_json_file)


def get_open_questions(questions, open_questions):
    return [get_question_message(questions, qid) for qid in open_questions]


def get_question_message(questions, qid):
    question = questions["questions"][qid]
    attachment = None
    if "attachment" in question:
        attachment = os.path.join(CONTENT_FOLDER, question["attachment"])
    return "Question {}: {}".format(qid, question["text"]), attachment


def get_question_answer(questions, qid):
    return questions["questions"][qid]["answer"]


async def send_open_questions(client, chat_id, questions, open_qids, prefix=""):
    await client.send_message(chat_id, prefix + "To answer a question, send a message \"answerX Y\" here where X is the question number and Y is the answer.\nThe open questions are:")
    open_questions = get_open_questions(questions, open_qids)
    for question, attachment in open_questions:
        # await client.send_message(chat_id, question)
        await client.send_message(chat_id, question, file=attachment)
    # await client.send_file(chat_id, 'attachments/pblock.png', caption="Attachment test")


async def get_channel_admin_ids(chat_id):
    admins = await client.get_participants(chat_id, filter=ChannelParticipantsAdmins)
    return [user.id for user in admins]


# listen to anytime the bot is added to a group and add it to the list of teams
# Technically, this isn't really necessary. For one, when creating a new group
# with the bot immediately in it, the channel is not added.
# However, whenever a message is sent in the chat, the channel is added anyway.
# But it has the advantage that the person adding the bot becomes an admin.
@client.on(events.ChatAction)
async def chat_action(event):
    if event.user_added:
        admin_id = event.added_by.id
        chat_id = event.chat_id
        chat_name = event.chat.title
        admin_ids = await get_channel_admin_ids(chat_id)
        add_new_channel(chat_id, chat_name, [admin_id] + admin_ids)


@client.on(events.NewMessage())
async def my_event_handler(event):
    chat_id = event.chat_id
    sender_id = event.sender_id
    text = event.message.message
    if not chat_id in team_channels:
        admin_ids = await get_channel_admin_ids(chat_id)
        add_new_channel(chat_id, event.chat.title, admin_ids)

    team_name = team_channels[chat_id]["name"]
    questions = json.load(open(QUESTIONS_JSON_FILE, "r"))
    n_questions = len(questions["questions"])
    team_json_file = get_progress_file(chat_id)
    team_vars = json.load(open(team_json_file, "r"))

    admins = team_channels[chat_id]["admins"]

    # Student is trying to submit an answer: answerX Y
    if text[:6].lower() == "answer":  # We accept any capitalization of "answer"
        # Spaces between answer and X are fine.
        answer_split = text[6:].split()
        if len(answer_split) != 2:
            await event.reply("I don't understand your answer \"{}\"".format(text))
            return
        answer_id_txt = answer_split[0]
        if (answer_id_txt[-1] == ":"):
            answer_id_txt = answer_id_txt[:-1]  # Allow semicolon after X

        # parse question ID and answer value
        try:
            answer_value = int(answer_split[1])
            answer_id = int(answer_id_txt)  # TODO: error handling
        except:
            await event.reply("I don't understand \"{}\"".format(text))
            return

        # Check the answer number and if valid, check the answer.
        if answer_id >= n_questions or answer_id < 0:
            # Invalid answer id
            await event.reply("There is no question " + str(answer_id))
        elif answer_id in team_vars["open_questions"]:
            # Valid open question.
            if answer_value == get_question_answer(questions, answer_id):
                # Answered correctly. Update variables.
                team_vars["n_solved"] += 1
                msg = "Your answer to question {} is correct! 1 token \U0001F31F".format(
                    answer_id)
                if enable_motivationals and answer_id in motivationals["special"]:
                    print(motivationals["special"][answer_id])
                    await event.reply(msg, file=motivationals["special"][answer_id])
                elif enable_motivationals and team_vars["n_solved"] in motivationals["regular"]:
                    await event.reply(msg, file=motivationals["regular"][team_vars["n_solved"]])
                else:
                    await event.reply(msg)
                team_vars["open_questions"].remove(answer_id)
                next_question_id = team_vars["n_solved"] + \
                    len(team_vars["open_questions"])
                prefix = ""  # Message to put before the listing of open questions
                if next_question_id < n_questions:
                    team_vars["open_questions"].append(next_question_id)
                    prefix = "You have unlocked a new question!\n\n"
                elif len(team_vars["open_questions"]) > 0:
                    prefix = "You have already unlocked all questions. Try to solve the remaining open ones!\n\n"
                else:
                    await client.send_message(chat_id, "Congrats! You have solved all questions!", file=motivationals["final"])
                json.dump(team_vars, open(get_progress_file(chat_id), "w"))

                # Print open questions if any remain:
                if len(team_vars["open_questions"]) != 0:
                    await send_open_questions(client, chat_id, questions, team_vars["open_questions"], prefix)
            else:
                # Wrong answer.
                await event.reply("Your answer ({}) to question {} is incorrect. :(".format(answer_value, answer_id))
        elif answer_id < team_vars["n_solved"] + len(team_vars["open_questions"]):
            # already solved before
            await event.reply("Your team has already solved question " + str(answer_id))
        else:
            # Trying to answer question that's not unlocked yet
            await event.reply("Question " + str(answer_id) + " is not available yet.")
    elif text[:9].lower() == "questions":
        # Post the list of open questions for the team
        await send_open_questions(client, chat_id, questions, team_vars["open_questions"])
    # await get_admins()
    elif text[:7] == "!!reset" and sender_id in admins:
        copyfile(get_progress_file("blank"), team_json_file)
        await event.reply("Progress for Team {} has been reset.".format(team_name))
    elif text[:7] == "!!reset" and sender_id not in admins:
        await event.reply("You are not an admin.")
    if text[:11] == "!!standings" and sender_id in admins:
        comp_id = text[11:].strip()
        # Show the current ranking between the teams
        ranking = []
        for team_id, team_data in team_channels.items():
            if not comp_id or ("competitions" in team_data and comp_id in team_data["competitions"]):
                team_json_file = get_progress_file(team_id)
                team_vars = json.load(open(team_json_file, "r"))
                ranking.append((team_vars["n_solved"], team_data["name"]))
        ranking.sort(reverse=True)
        if ranking:
            text_ranking = '\n'.join(
                "Team {}: {} questions solved".format(r[1], r[0]) for r in ranking)
            await event.reply(text_ranking)
        else:
            await event.reply(f"Unknown competition id \'{comp_id}\'")
    elif text[:11] == "!!standings" and sender_id not in admins:
        await event.reply("You are not an admin.")
    if text[:10] == "!!joincomp" and sender_id in admins:
        comp_id = text[10:].strip()
        if not "competitions" in team_channels[chat_id]:
            team_channels[chat_id]["competitions"] = [comp_id]
            write_team_channels()
        elif comp_id not in team_channels[chat_id]["competitions"]:
            team_channels[chat_id]["competitions"].append(comp_id)
            write_team_channels()
        await event.reply(f"Joined competition \'{comp_id}\'")
    elif text[:10] == "!!joincomp" and sender_id not in admins:
        await event.reply("You are not an admin.")
    if text[:7] == "!!intro":
        msg = "Welcome to the puzzle competition! Try to solve as many puzzles as you can " + \
            "in your team. Your team will always have 4 open puzzles available to solve. " + \
            "Whenever you solve a puzzle, you unlock a new one for your team. You can " + \
            "work on one puzzle together, or on different puzzles at the same time. " + \
            "Your team gets 1 \U0001F31F (token) for each puzzle you solve!\n\n" + \
            "If a question is not clear, please ask in the chat!\n\n" + \
            "Send a message \"questions\" to start.\n\n""" + \
            "To answer a question, send a message \"answerX Y\" here where X is the question number and Y is the answer."
        await client.send_message(chat_id, msg)

client.start(bot_token=bot_token)
get_team_channels()
setup_progress_files()
get_motivationals()
client.run_until_disconnected()
