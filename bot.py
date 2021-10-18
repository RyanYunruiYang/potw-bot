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
potw_file = open('potw.yaml')
potw_contents = yaml.load(potw_file, Loader = yaml.FullLoader)
current_potw = potw_contents['current-potw']

@bot.event
async def on_message(message):
    await bot.process_commands(message)


@bot.command(brief="Print the current POTW")
async def potw(ctx):
    await ctx.channel.send(current_potw['text'])


@bot.command(brief="Submit answer to the current POTW")
async def submit(ctx, arg):
    submitter = ctx.author.id
    if current_potw['simple-solution'] == True:
        if arg == current_potw['solution']:
            # assign points
            func.assign_points(submitter, current_potw['points'])
            await ctx.channel.send("Your solution was correct; you have gained " + str(current_potw['points']) + " points!")
        else:
            await ctx.channel.send("Your solution was incorrect; please try again.")
    else:
        # send solution to mods
        await ctx.channel.send("Thanks! Your solution was sent to the mods for review.")
        channel = bot.get_channel(899463961836142664) # organizer-only channel 
        await channel.send(f"From <@{submitter}>: " + str(arg))


@bot.command()
@commands.has_role('organizer')
async def assign_point(ctx, user, pointvalue):
    # add point value to database
    func.assign_points(user, pointvalue)
    await ctx.channel.send(f"{pointvalue} points has been assigned to <@{user}>")

@bot.command(brief="Print leaderboard")
@commands.has_role('organizer')
async def leaderboard(ctx):
    with open('leaderboard.yaml', 'r') as f:
        leaderboard = yaml.load(f, Loader = yaml.FullLoader)
    sorted_leaderboard = sorted(leaderboard, key=lambda d: d['points'], reverse=True)

    message = ""

    for i in range(0, len(sorted_leaderboard)):
        message += f"{i+1} | <@{sorted_leaderboard[i]['userID']}> with {sorted_leaderboard[i]['points']} points \n"
    
    await ctx.channel.send(message)

#TODO: let people know how many points they have
#TODO: find way to incorporate username without pinging people
#TODO: problem proposals (maybe not)

# run the bot
bot.run(TOKEN)


