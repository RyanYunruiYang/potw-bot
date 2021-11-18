# external Packages
import os
import discord
import yaml
import func
from dotenv import load_dotenv
from discord.ext import commands

# local Files
import utils

# create the bot
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="!")
client = discord.Client()

# load potw yaml file
with open('potw.yaml', 'r') as f:
    potw_contents = yaml.load(f, Loader = yaml.FullLoader)
current_potw = potw_contents['current-potw']

@bot.event
async def on_message(message):
    await bot.process_commands(message)

# user commands

@bot.command(brief="Print the current POTW")
async def potw(ctx):
    await ctx.channel.send(f"Field: {current_potw['field']}\nProblem ID: {current_potw['potw-id']}\nAuthor: {current_potw['author']}\nEffective Date: {current_potw['effective-date']}\nDifficulty: {current_potw['difficulty']} jalapeños\nProblem statement: {current_potw['text']}")


@bot.command(brief="Submit answer to the current POTW")
async def submit(ctx):
    submitter = ctx.author.id
    answer = str(ctx.message.content)

    if current_potw['simple-solution'] == True:
        if answer == current_potw['solution']:
            # assign points
            func.assign_points(submitter, current_potw['points'])
            await ctx.channel.send("Your solution was correct; you have gained " + str(current_potw['points']) + " points!")
        else:
            await ctx.channel.send("Your solution was incorrect; please try again.")
    else:
        # send solution to mods
        await ctx.channel.send("Thanks! Your solution was sent to the mods for review.")
        channel = bot.get_channel(899463961836142664) # organizer-only channel 
        await channel.send(f"From <@{submitter}>: " + str(answer))

@bot.command(brief="Questions/comments? Send a message to the organizers")
async def ask(ctx):
    submitter = ctx.author.id
    msg = str(ctx.message.content)

    await ctx.channel.send("Message was sent to mods.")
    channel = bot.get_channel(899463961836142664) # organizer-only channel 
    await channel.send(f"From <@{submitter}>: " + str(msg))


@bot.command(brief="Print leaderboard") # top 10 people only + user
async def leaderboard(ctx):
    with open('leaderboard.yaml', 'r') as f:
        leaderboard = yaml.load(f, Loader = yaml.FullLoader)
    sorted_leaderboard = sorted(leaderboard, key=lambda d: d['points'], reverse=True)

    message = ""

    for i in range(0, len(sorted_leaderboard)):
        if i < 10:
            message += f"{i+1} | `<@{sorted_leaderboard[i]['userID']}>` with {sorted_leaderboard[i]['points']} points\n"
        elif ctx.message.author.id == sorted_leaderboard[i]['userID']:
            message += f".\n.\n.\nYOU: {i+1} | `<@{sorted_leaderboard[i]['userID']}>` with {sorted_leaderboard[i]['points']} points"
            break

    await ctx.channel.send(message)



# mod commands

@bot.command(brief="Assign points (user ID, points to assign)")
@commands.has_role('organizer')
async def assign_point(ctx, user: discord.User, pointvalue, *, msg):
    # add point value to database
    func.assign_points(user.id, pointvalue)
    await ctx.channel.send(f"{pointvalue} points has been assigned to <@{user.id}>")

    await user.send(f"You have just been awarded {pointvalue} out of {current_potw['points']} possible points! " + str(msg))

@bot.command(brief="Bad Bot")
async def badbot(ctx):
    with open('botpoints.txt', 'r+') as f:
        points = f.readlines()[0]
    
    if points !="":
        points = int(points)
    else:
        points = 0
    
    points-=5

    message = "OMG I AM SO BAD!!!!\nBot's current points are: "+str(points)

    with open('botpoints.txt', 'w') as f:
        f.truncate(0)
        f.write(str(points))

    await ctx.channel.send(message)

@bot.command(brief="Cool Bot")
async def coolbot(ctx):
    with open('botpoints.txt', 'r+') as f:
        points = f.readlines()[0]
    
    if points !="":
        points = int(points)
    else:
        points = 0
    
    points+=5

    message = "YAYE IKR IM SO COOOOL!!!!\nBot's current points are: "+str(points)

    with open('botpoints.txt', 'w') as f:
        f.truncate(0)
        f.write(str(points))

    await ctx.channel.send(message)

@bot.command(brief="Sid the Science Kid")
async def sidiscool(ctx):
    message = "Correct."
    await ctx.channel.send(message)

@bot.command(brief="Sidharth Vader")
async def sidisnotcool(ctx):
    message = ":("
    await ctx.channel.send(message)


@bot.command(brief="Create a new POTW")
@commands.has_role('organizer')
async def create_potw(ctx):
    problem_statement = str(ctx.message.content)

    old_potw = {
        'potw-id': int(current_potw['potw-id']),
        'field': str(current_potw['field']),
        'author': str(current_potw['author']),
        'effective-date': str(current_potw['effective-date']),
        'text': str(current_potw['text']),
        'simple-solution': bool(current_potw['simple-solution']),
        'solution': str(current_potw['solution']),
        'points': float(current_potw['points']),
        'difficulty': int(current_potw['difficulty'])
    }

    potw_contents[f"potw-{current_potw['potw-id']}"] = old_potw

    current_potw['potw-id'] = int(current_potw['potw-id']) + 1
    current_potw['text'] = problem_statement[13:]

    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel

    await ctx.channel.send("Enter field/department:")
    current_potw['field'] = str((await bot.wait_for('message', check=check)).content)

    await ctx.channel.send("Enter author name:")
    current_potw['author'] = str((await bot.wait_for('message', check=check)).content)

    await ctx.channel.send("Enter effective date (today) (MM/DD/YYYY):")
    current_potw['effective-date'] = str((await bot.wait_for('message', check=check)).content)

    await ctx.channel.send("Simple solution? (Y/N):")
    is_simple = str((await bot.wait_for('message', check=check)).content)
    if is_simple == 'Y':
        current_potw['simple-solution'] = True
    else:
        current_potw['simple-solution'] = False

    await ctx.channel.send("Enter solution:")
    current_potw['solution'] = str((await bot.wait_for('message', check=check)).content)

    await ctx.channel.send("Enter point value:")
    current_potw['points'] = float((await bot.wait_for('message', check=check)).content)

    await ctx.channel.send("Enter difficulty (# of jalapeños, 1-4):")
    current_potw['difficulty'] = int((await bot.wait_for('message', check=check)).content)

    with open('potw.yaml', 'w') as f:
        yaml.dump(potw_contents, f)

    await ctx.channel.send("New POTW has successfully been imported and put into use.")


@bot.command(brief="Edit the current POTW; however, if you're making major changes, creating a new POTW would be better")
@commands.has_role('organizer')
async def edit_potw(ctx, arg, *, content):
    if arg == 'field':
        potw_contents['current-potw']['field'] = str(content)
        await ctx.channel.send("Field has been edited.")
    elif arg == 'author':
        potw_contents['current-potw']['author'] = str(content)
        await ctx.channel.send("Author has been edited.")
    elif arg == 'effective-date':
        potw_contents['current-potw']['effective-date'] = str(content)
        await ctx.channel.send("Date has been edited.")
    elif arg == 'text':
        potw_contents['current-potw']['text'] = str(content)
        await ctx.channel.send("Statement has been edited.")
    elif arg == 'simple-solution':
        potw_contents['current-potw']['simple-solution'] = bool(content)
        await ctx.channel.send("Simpleness has been edited.")
    elif arg == 'solution':
        potw_contents['current-potw']['solution'] = str(content)
        await ctx.channel.send("Solution has been edited.")
    elif arg == 'points':
        potw_contents['current-potw']['points'] = float(content)
        await ctx.channel.send("Number of points has been edited.")
    elif ag == 'difficulty':
        potw_contents['current-potw']['difficulty'] = int(content)
        await ctx.channel.send("Difficulty has been edited.")
    else:
        await ctx.channel.send("Check spelling?")


@bot.command(brief="Print solution of the current POTW")
@commands.has_role('organizer')
async def solution(ctx):
    await ctx.channel.send(current_potw['solution'])


@bot.command(brief="Send any DM message to a user")
@commands.has_role('organizer')
async def dm_user(ctx, user:discord.User, *, msg):
    await user.send(msg)
    await ctx.channel.send("DM sent.")

# run the bot
bot.run(TOKEN)


