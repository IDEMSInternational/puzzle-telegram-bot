from telethon import TelegramClient, events
import json
from shutil import copyfile
import os
from dotenv import load_dotenv
from motivationals import motivationals, special_motivationals, final_motivational

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


def get_team_channels():
    tmp = {}
    with open("channels.json", "r") as f:
        tmp = json.load(f)
        for key, value in tmp.items():
            team_channels[key] = value[0]
    print(team_channels)


# listen to anytime the bot is added to a group and add it to the list of teams


# teams (=channels) that appear in the standings.
true_teams = []


def get_true_teams():
    tmp = {}
    with open("channels.json", "r") as f:
        tmp = json.load(f)
        for team_name in tmp.keys():
            true_teams.append(team_name)

    print(true_teams)


# People who can e.g. reset progress
admins = []


def get_admins():
    tmp = {}
    with open("channels.json", "r") as f:
        tmp = json.load(f)
        for _, admin in tmp.items():
            admins.append(admin[1])
    print(admins)


# Make a blank file with progress for each team, if none exists
def setup_progress_files():
    for tame_name, _ in team_channels.items():
        team_json_file = "progress_" + tame_name + ".json"
        if not os.path.isfile(team_json_file):
            copyfile("team_reset.json", team_json_file)


def get_open_questions(questions, open_questions):
    return [get_question_message(questions, qid) for qid in open_questions]


def get_question_message(questions, qid):
    question = questions["questions"][qid]
    attachment = None
    if "attachment" in question:
        attachment = question["attachment"]
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


# , pattern=r'(?i).*heck',  pattern=r'\.save', from_users=123456789
@client.on(events.NewMessage())
async def my_event_handler(event):
    # chat = await event.get_chat()
    # sender = await event.get_sender()
    chat_id = event.chat_id
    sender_id = event.sender_id
    text = event.message.message
    if chat_id in team_channels.values():

        team_name = list(team_channels.keys())[
            list(team_channels.values()).index(chat_id)]
        questions = json.load(open("questions.json", "r"))
        n_questions = len(questions["questions"])
        team_json_file = "progress_" + team_name + ".json"
        team_vars = json.load(open(team_json_file, "r"))

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
                    if enable_motivationals and answer_id in special_motivationals:
                        await event.reply(msg, file=special_motivationals[answer_id])
                    elif enable_motivationals and team_vars["n_solved"] in motivationals:
                        await event.reply(msg, file=motivationals[team_vars["n_solved"]])
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
                        await client.send_message(chat_id, "Congrats! You have solved all questions!", file=final_motivational)
                    json.dump(team_vars, open(
                        "progress_" + team_name + ".json", "w"))

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
            copyfile("team_reset.json", team_json_file)
            await event.reply("Progress for Team {} has been reset.".format(team_name))
        elif text[:7] == "!!reset" and sender_id not in admins:
            await event.reply("You are not an admin.")
    if text[:11] == "!!standings" and sender_id in admins:
        # Show the current ranking between the teams
        ranking = []
        for team_name in team_channels.keys():
            team_json_file = "progress_" + team_name + ".json"
            team_vars = json.load(open(team_json_file, "r"))
            if team_name in true_teams:
                ranking.append((team_vars["n_solved"], team_name))
        ranking.sort(reverse=True)
        text_ranking = '\n'.join(
            "Team {}: {} questions solved".format(r[1], r[0]) for r in ranking)
        await event.reply(text_ranking)
    elif text[:11] == "!!standings" and sender_id not in admins:
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
get_true_teams()
get_admins()
setup_progress_files()
client.run_until_disconnected()
