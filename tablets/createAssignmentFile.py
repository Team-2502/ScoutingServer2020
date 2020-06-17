import tbapy
import pyrebase

import sensitiveInfo


firebase = pyrebase.initialize_app(sensitiveInfo.firebase_info_dev_2021())
database = firebase.database()

# Setup for tbapy
tba = tbapy.TBA(sensitiveInfo.tba_api_key())
event = "2020mndu2"

# Get a list of all qualifying matches at an event
try:
    matches = [match for match in tba.event_matches(event, simple=True) if match['comp_level'] == 'qm']

# TODO Make this except clause more specfic
except:
    print("Error getting matches from TBA, check event and API keys.")
    exit(1)

full_assignments = {}
ds_order = ["Red 1", "Red 2", "Red 3", "Blue 1", "Blue 2", "Blue 3"]

for match in matches:
    # Query TBA for info about each match
    match_num = match['match_number']
    redTeams = match['alliances']['red']['team_keys']
    redTeams = [int(team[3:]) for team in redTeams]
    blueTeams = match['alliances']['blue']['team_keys']
    blueTeams = [int(team[3:]) for team in blueTeams]
    teams = redTeams + blueTeams

    assignments = {}
    numScouts = 6
    scouts = ['scout' + str(x) for x in range(1, numScouts + 1)]

    # Assign each scout to a team
    for i in range(len(scouts)):
        assignments[scouts[i]] = {'team': teams[(i % 6)], 'alliance': (ds_order[(i % 6)])}

    full_assignments["QM "+str(match_num)] = assignments

# Upload assignments to Firebase
database.child("config").child("scoutAssignments").set(full_assignments)
