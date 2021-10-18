import os
import yaml
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!")

def assign_points(user, points):
    with open('leaderboard.yaml', 'r') as f:
        leaderboard = yaml.load(f, Loader = yaml.FullLoader)

    with open('potw.yaml', 'r') as f:
        potw_contents = yaml.load(f, Loader = yaml.FullLoader)
    current_potw = potw_contents['current-potw']

    user_in_leaderboard = False

    for person in leaderboard:
        if str(person['userID']) == str(user):
            person['points'] = int(person['points']) + int(points)
            solved_list = person['solved-list']
            solved_list.append(current_potw['potw-id'])
            person['solved-list'] = solved_list
            user_in_leaderboard = True

    if user_in_leaderboard == False:
        person = {'points': int(points), 'solved-list': [current_potw['potw-id']], 'userID': int(user), 'username': bot.get_user(int(user))}
        leaderboard.append(person)

    with open('leaderboard.yaml', 'w') as f:
        yaml.dump(leaderboard, f)