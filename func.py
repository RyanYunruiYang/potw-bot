import yaml

def assign_points(user, points):
	f = open('leaderboard.yaml')
	leaderboard = yaml.load(f, Loader = yaml.FullLoader)

	potw_file = open('potw.yaml')
	potw_contents = yaml.load(potw_file, Loader = yaml.FullLoader)
	current_potw = potw_contents['current-potw']

	for username in leaderboard:
	    if username == user:
	    	username['points'] += points
	    	
	    	solved_list = username['solved-list']
	    	solved_list.append(current_potw['potw-id'])
	    	username['solved-list'] = solved_list

	yaml.dump(leaderboard, f)
	f.close()