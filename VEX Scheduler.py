import random

file = open("schedule.txt", 'r')

team_dict = {}

biased_teams = ["39C", "91F", "502X", "1437X", "1588A", "1747A", "2660X", "2990E", "3796E", "4478D" "4828W", "5999A", "6210X",
                "6603A", "7110Y", "8047F", "8349A", "8756A", "8995J" "9142W", "18628A", "23218A", "33472D", "36830W", "51617A", "55885S", "62880A", "66659A", "89040A", "96944B"]

pref_team_1_list = []
pref_team_2_list = []

line = file.readline()
while line:
    teams = []
    for word in line.split():
        if 'Q' in word or word in ["VEX", "USAF", "FusionIRX", "Fri", "Sat", "AM", "PM"] or ":" in word:
            pass
        else:
            teams.append(word)

    for team in teams:
        if team not in team_dict:
            if team in biased_teams:
                team_dict[team] = -1
            else:
                team_dict[team] = 0

    pref_team_1 = min(teams, key = lambda team: team_dict[team])
    teams.pop(teams.index(pref_team_1))
    pref_team_2 = min(teams, key = lambda team: team_dict[team])

    team_dict[pref_team_1] += 1
    team_dict[pref_team_2] += 1

    pref_team_1_list.append(pref_team_1)
    pref_team_2_list.append(pref_team_2)
        
    line = file.readline()

print("SLOT 1")
for i in pref_team_1_list:
    print(i)

print("\n\nSLOT 2")
for i in pref_team_2_list:
    print(i)

