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
    await ctx.channel.send(f"Field: {current_potw['field']}\nProblem ID: {current_potw['potw-id']}\nAuthor: {current_potw['author']}\nDifficulty: {current_potw['difficulty']} jalapeños\nProblem statement: {current_potw['text']}")


@bot.command(brief="Submit answer to the current POTW")
async def submit(ctx):
    submitter = ctx.author.id
    answer = str(ctx.message.content)

    if func.check_solved(submitter, current_potw['potw-id']) == True:
        await ctx.channel.send("You have alreay solved this week's problem!")
        return

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


# mod commands
@bot.command(brief="Announce the current POTW to #potw")
@commands.has_role('organizer')
async def announce_potw(ctx):
    channel = bot.get_channel(891482447580123137) #announcements
    await ctx.channel.send(f"""Field: {current_potw['field']}
    Problem ID: {current_potw['potw-id']}
    Author: {current_potw['author']}
    Difficulty: {current_potw['difficulty']} jalapeños
    Problem statement: {current_potw['text']}""")


@bot.command(brief="Assign points (user ID, points to assign)")
@commands.has_role('organizer')
async def assign_point(ctx, user: discord.User, pointvalue):
    # add point value to database
    func.assign_points(user.id, pointvalue)
    await ctx.channel.send(f"{pointvalue} points has been assigned to <@{user.id}>")

    await user.send(f"You have just been awarded {pointvalue} points!")


@bot.command(brief="Send a rejection message to the user")
@commands.has_role('organizer')
async def reject_solution(ctx, user: discord.User):
    await user.send("Sorry, your solution to the current POTW has been rejected by the mods. Please try again, or contact Jewon or Ryan for more info.")


@bot.command(brief="Print leaderboard") # top 10 people only + user
async def leaderboard(ctx):
    with open('leaderboard.yaml', 'r') as f:
        leaderboard = yaml.load(f, Loader = yaml.FullLoader)
    sorted_leaderboard = sorted(leaderboard, key=lambda d: d['points'], reverse=True)

    message = ""

    for i in range(0, len(sorted_leaderboard)):
        if i < 10:
            message += f"{i+1} | <@{sorted_leaderboard[i]['userID']}> with {sorted_leaderboard[i]['points']} points\n"
        elif ctx.message.author.id == sorted_leaderboard[i]['userID']:
            message += f".\n.\n.\nYOU: {i+1} | <@{sorted_leaderboard[i]['userID']}> with {sorted_leaderboard[i]['points']} points"
            break

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
        'points': int(current_potw['points']),
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
    current_potw['points'] = int((await bot.wait_for('message', check=check)).content)

    await ctx.channel.send("Enter difficulty (# of jalapeños, 1-4):")
    current_potw['difficulty'] = int((await bot.wait_for('message', check=check)).content)

    with open('potw.yaml', 'w') as f:
        yaml.dump(potw_contents, f)

    await ctx.channel.send("New POTW has successfully been imported and put into use.")

'''
@bot.command()
async def test(ctx, userID):
    user = await bot.fetch_user(int(userID))
    await ctx.channel.send(f"{user.display_name}\n{user.name}\n{user.discriminator}")
'''

# run the bot
bot.run(TOKEN)


