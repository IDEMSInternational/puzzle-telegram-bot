from telethon import TelegramClient, events
import json
from shutil import copyfile
import os
from motivationals import motivationals, special_motivationals, final_motivational

import logging
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

enable_motivationals = True

team_channels = {
    -1001293467797: "Treasure Hunt Test",  # https://t.me/+O3n38sULb0BlZDA8
}

# teams (=channels) that appear in the standings.
true_teams = ["Treasure Hunt Test"]

# People who can e.g. reset progress
admins = {
    123456789,   # some user
}

# Use your own values from my.telegram.org
api_id = -1
api_hash = ''
bot_token = ''
client = TelegramClient('NameOfYour_bot', api_id, api_hash)

# Make a blank file with progress for each team, if none exists
for _,team_id in team_channels.items():
    team_json_file = "team_" + team_id + ".json"
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

@client.on(events.NewMessage())  #, pattern=r'(?i).*heck',  pattern=r'\.save', from_users=123456789
async def my_event_handler(event):
    chat = await event.get_chat()
    sender = await event.get_sender()
    chat_id = event.chat_id
    sender_id = event.sender_id
    text = event.message.message
    if chat_id in team_channels:
        # print(chat_id, sender_id)
        # print(event.message.message)

        team_id = team_channels[chat_id]
        questions = json.load(open("questions.json", "r"))
        n_questions = len(questions["questions"])
        team_json_file = "team_" + team_id + ".json"
        team_vars = json.load(open(team_json_file, "r"))

        # Student is trying to submit an answer: answerX Y
        if text[:6].lower() == "answer":  # We accept any capitalization of "answer"
            answer_split = text[6:].split()  # Spaces between answer and X are fine.
            if len(answer_split) != 2:
                await event.reply("I don't understand your answer \"{}\"".format(text))
                return
            answer_id_txt = answer_split[0]
            if (answer_id_txt[-1] == ":"):
                answer_id_txt = answer_id_txt[:-1]  # Allow semicolon after X

            # parse question ID and answer value
            try:
                answer_value = int(answer_split[1])
                answer_id = int(answer_id_txt) # TODO: error handling
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
                    msg = "Your answer to question {} is correct! 1 token \U0001F31F".format(answer_id)
                    if enable_motivationals and answer_id in special_motivationals:
                        await event.reply(msg, file=special_motivationals[answer_id])
                    elif enable_motivationals and team_vars["n_solved"] in motivationals:
                        await event.reply(msg, file=motivationals[team_vars["n_solved"]])
                    else:
                        await event.reply(msg)
                    team_vars["open_questions"].remove(answer_id)
                    next_question_id = team_vars["n_solved"] + len(team_vars["open_questions"])
                    prefix = ""  # Message to put before the listing of open questions
                    if next_question_id < n_questions:
                        team_vars["open_questions"].append(next_question_id)
                        prefix = "You have unlocked a new question!\n\n"
                    elif len(team_vars["open_questions"]) > 0:
                        prefix = "You have already unlocked all questions. Try to solve the remaining open ones!\n\n"
                    else:
                        await client.send_message(chat_id, "Congrats! You have solved all questions!", file=final_motivational)
                    json.dump(team_vars, open("team_" + team_id + ".json", "w"))

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
        elif text[:9] == "questions":
            # Post the list of open questions for the team
            await send_open_questions(client, chat_id, questions, team_vars["open_questions"])
        elif text[:7] == "!!reset" and sender_id in admins:
            copyfile("team_reset.json", team_json_file)
            await event.reply("Progress for Team {} has been reset.".format(team_id))
    if text[:11] == "!!standings" and sender_id in admins:
        # Show the current ranking between the teams
        ranking = []
        for _,team_id in team_channels.items():
            team_json_file = "team_" + team_id + ".json"
            team_vars = json.load(open(team_json_file, "r"))
            if team_id in true_teams:
                ranking.append((team_vars["n_solved"], team_id))
        ranking.sort(reverse=True)
        text_ranking = '\n'.join("Team {}: {} questions solved".format(r[1], r[0]) for r in ranking)
        await event.reply(text_ranking)
    if text[:7] == "!!intro" and sender_id in admins:
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
client.run_until_disconnected()
