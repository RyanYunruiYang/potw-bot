import os
import yaml
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!")

def check_solved(user, potwID):
    with open('leaderboard.yaml', 'r') as f:
        leaderboard = yaml.load(f, Loader = yaml.FullLoader)

    with open('potw.yaml', 'r') as f:
        potw_contents = yaml.load(f, Loader = yaml.FullLoader)
    current_potw = potw_contents['current-potw']

    for person in leaderboard:
        if str(person['userID']) == str(user):
            for solved in person['solved-list']:
                if solved == potwID:
                    return True

    return False

def assign_points(userID, points):
    user = bot.fetch_user(int(userID))

    with open('leaderboard.yaml', 'r') as f:
        leaderboard = yaml.load(f, Loader = yaml.FullLoader)

    with open('potw.yaml', 'r') as f:
        potw_contents = yaml.load(f, Loader = yaml.FullLoader)
    current_potw = potw_contents['current-potw']

    user_in_leaderboard = False

    for person in leaderboard:
        if str(person['userID']) == str(userID):
            person['points'] = int(person['points']) + int(points)

            if check_solved(userID, current_potw['potw-id']) == False:
                solved_list = person['solved-list']
                solved_list.append(current_potw['potw-id'])
                person['solved-list'] = solved_list
            
            user_in_leaderboard = True

    if user_in_leaderboard == False:

        person = {'points': int(points), 'solved-list': [current_potw['potw-id']], 'userID': userID, 'username': f"{user.name}#{user.discriminator}"}
        leaderboard.append(person)

    with open('leaderboard.yaml', 'w') as f:
        yaml.dump(leaderboard, f)
