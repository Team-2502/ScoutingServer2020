import os
import json


def get_timds():
    homeDir = os.path.expanduser('~')
    TIMDs = [timd for timd in os.listdir(os.path.join(homeDir, 'MNDU2-2020Server/cache/TIMDs')) if timd != '.DS_Store']
    return [json.loads(open(os.path.join(homeDir, 'MNDU2-2020Server/cache/TIMDs/', TIMD)).read()) for TIMD in TIMDs]


timds = get_timds()
scout_ranks = {}
for timd in timds:
    scout = timd['header']['scoutKey']
    if scout not in scout_ranks.keys():
        scout_ranks[scout] = 1
    else:
        scout_ranks[scout] += 1

for scout in scout_ranks.keys():
    print(scout + ": " + str(scout_ranks[scout]))

