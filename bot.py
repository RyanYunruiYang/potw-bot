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
    if current_potw['simple-solution'] == True:
        if arg == current_potw['solution']:
            # assign points
            func.assign_points(bot.get_user(user_id), current_potw['points'])
            await ctx.channel.send("Your solution was correct; you have gained " + str(current_potw['points']) + " points!")
    else:
        # send solution to mods
        await ctx.channel.send("Thanks! Your solution was sent to the mods for review.")

@bot.command()
@commands.has_rile('Mod')
async def assign_point(ctx, user, pointvalue):
    # add point value to database
    await ctx.channel.send(str(pointvalue) + " has been assigned to user " + user)

# run the bot
bot.run(TOKEN)


