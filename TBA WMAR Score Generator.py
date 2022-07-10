#to run this program, please install Python's Requests library
#this program fetches alliance and event data from The Blue Alliance to generate a set of WMAR scores
#the output is a set of 8 subsets of WMAR scores, delimited by "---"
#each subset consists of data for a specific alliance
#the first subset consists of Alliance 1 scores, the second consists of Alliance 2 scores, and so on

import requests

authKey = "QC6gue0B4LwDV8PzL0i07cVOexX3kR5ym56JoRhrpVxsD4cdWRFFawFTwrd1nLbG"
header = {"X-TBA-Auth-Key": authKey}

year = "2019"

eventWeeks = [0, 1, 3, 5, 6]

sampleAlliances = []
wmars = []

for i in range(0, 8):
    wmars.append([])

eventsRaw = requests.get("https://www.thebluealliance.com/api/v3/events/" +year, headers=header).json()
eventKeys = []

#get events
for event in eventsRaw:
    if event["week"] in eventWeeks:
        eventKeys.append(event["key"])

eventNumber = 0

#get alliances at events
for eventKey in eventKeys:
    #get event alliances
    alliancesRaw = requests.get("https://www.thebluealliance.com/api/v3/event/" +eventKey +"/alliances", headers=header).json()

    #discard cross-division events (containing duplicate alliances)
    if alliancesRaw[0]["name"] != "Alliance 1":
        continue
    
    #get event CCWM
    oprsRaw = requests.get("https://www.thebluealliance.com/api/v3/event/" +eventKey +"/oprs", headers=header).json()
    eventCcwms = oprsRaw["ccwms"]

    #sort CCWM values
    ccwmsSorted = sorted(eventCcwms[team] for team in eventCcwms)
    
    #find median CCWM
    if len(ccwmsSorted) % 2 == 0:
        ccwmMedian = (ccwmsSorted[int(len(ccwmsSorted) / 2 - 1)] + ccwmsSorted[int(len(ccwmsSorted) / 2)]) / 2
    else:
        ccwmMedian = ccwmsSorted[int(len(ccwmsSorted) / 2)]

    for seed in range(1, 9):
        #populate alliance info
        teamKeys = [alliancesRaw[seed - 1]["picks"][i] for i in range(3)]

        captainCcwm = eventCcwms[teamKeys[0]]
        allianceCcwm = 0

        for team in teamKeys:
            allianceCcwm += eventCcwms[team]
        
        #discard if prediction has low confidence
        if abs(allianceCcwm) < 0.5:
            continue

        qfWinMargins = []

        #find average win margins in quarterfinals
        while len(qfWinMargins) < 2:
            matchesRaw = requests.get("https://www.thebluealliance.com/api/v3/team/" +teamKeys[0] +"/event/" +eventKey +"/matches/simple", headers=header).json()

            #get match win margins
            for match in matchesRaw:
                if match["comp_level"] == "qf":
                    if teamKeys[0] in match["alliances"]["blue"]["team_keys"]:
                        qfWinMargins.append(match["alliances"]["blue"]["score"] - match["alliances"]["red"]["score"])
                    else:
                        qfWinMargins.append(match["alliances"]["red"]["score"] - match["alliances"]["blue"]["score"])

            #check for backup teams if a team had to sub out
            if len(qfWinMargins) < 2 and alliancesRaw[seed - 1]["backup"]:
                teamKeys[teamKeys.index(alliancesRaw[seed - 1]["backup"]["out"])] = alliancesRaw[seed - 1]["backup"]["in"]
        
        meanQfWinMargin = sum(qfWinMargins) / len(qfWinMargins)
        
        #aggregate alliance information
        allianceData = {"seed": seed, "mean_qf_win_margin": meanQfWinMargin,"captain_ccwm": captainCcwm, "alliance_ccwm": allianceCcwm, "event_median_ccwm": ccwmMedian}
        sampleAlliances.append(allianceData)
    
    eventNumber += 1
    print("Fetched " +eventKey +" alliances, collected " +(str(round(100 * eventNumber / len(eventKeys)))) +"% of alliance data")

print("Sampled", len(sampleAlliances) ,"alliances")

#calculate WMAR scores
for alliance in sampleAlliances:
    #check sign of mean win margins and median CCWM
    if alliance["mean_qf_win_margin"] * alliance["event_median_ccwm"] >= 0:
        realityFactor = alliance["mean_qf_win_margin"] / alliance["alliance_ccwm"]
    else:
        realityFactor = alliance["alliance_ccwm"] / alliance["mean_qf_win_margin"]
    medianContribution = alliance["event_median_ccwm"] * realityFactor

    #check sign of mean win margins and captain CCWM
    if alliance["mean_qf_win_margin"] * alliance["captain_ccwm"] >= 0:
        realityFactor = alliance["mean_qf_win_margin"] / alliance["alliance_ccwm"]
    else:
        realityFactor = alliance["alliance_ccwm"] / alliance["mean_qf_win_margin"]

    captainContribution = alliance["captain_ccwm"] * realityFactor
    
    baselineAllianceWinMargin = captainContribution + 2 * medianContribution

    wmar = alliance["mean_qf_win_margin"] - baselineAllianceWinMargin
    wmars[alliance["seed"] - 1].append(wmar)

#print WMAR scores
for seedWmars in wmars:
    print("-----")
    for wmar in seedWmars:
        print(wmar)