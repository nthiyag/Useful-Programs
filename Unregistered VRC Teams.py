import requests

team_numbers = set()

print("Fetching...")
data_length = requests.get("https://api.vexdb.io/v1/get_teams?nodata=true").json()["size"]

print("Processing...")
for i in range(int(data_length/5000)+1):
    data = requests.get("https://api.vexdb.io/v1/get_teams?program=VRC&limit_number=5000&limit_start=" +str(5000*i))
    team_list = data.json()["result"]

    for team in team_list:
        if team["number"][-1].isalpha():
            n = -2
            while team["number"][n].isalpha():
                n -= 1
            n += 1
            team_numbers.add(int(team["number"][0:n]))
        else:
            team_numbers.add(int(team["number"]))

teams_printed = 0

print("Ready.\n")
for i in range(int(input("List team numbers under: "))):
    if i not in team_numbers:
        teams_printed += 1
        print(i, end=' ')
    if teams_printed == 10:
        teams_printed = 0
        print('')
            



