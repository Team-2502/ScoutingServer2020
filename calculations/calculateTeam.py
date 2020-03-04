import os
import json
import pyrebase

import sensitiveInfo
from utils import *

TOTAL_AVERAGE_DATA_FIELDS = {
    'avgCellsScored': 'cellsScoredTeleop',
    'avgCellsScoredHigh': 'cellsScoredHighTeleop',
    'avgCellsScoredLow': 'cellsScoredLowTeleop',
    'avgTimeIncap': 'timeIncap',
    'avgTimeDefending': 'timeDefending',
    'avgTOC': 'trueOffensiveContribution'
}

L3M_AVERAGE_DATA_FIELDS = {
    'l3mCellsScored': 'cellsScoredTeleop',
    'l3mCellsScoredHigh': 'cellsScoredHighTeleop',
    'l3mCellsScoredLow': 'cellsScoredLowTeleop',
    'l3mTimeIncap': 'timeIncap',
    'l3mTimeDefending': 'timeDefending'
}

P75_DATA_FIELDS = {
    'l3mCellsScored': 'cellsScoredTeleop',
    'l3mCellsScoredHigh': 'cellsScoredHighTeleop',
    'l3mCellsScoredLow': 'cellsScoredLowTeleop',
}

SD_DATA_FIELDS = {
    'SDCellsScored': 'cellsScoredTeleop',
    'SDCellsScoredHigh': 'cellsScoredHighTeleop',
    'SDCellsScoredLow': 'cellsScoredLowTeleop',
    'SDTOC': 'trueOffensiveContribution'
}

MAX_DATA_FIELDS = {
    'maxCellsScored': 'cellsScoredTeleop',
    'maxCellsScoredHigh': 'cellsScoredHighTeleop',
    'maxCellsScoredLow': 'cellsScoredLowTeleop',
    'maxTOC': 'trueOffensiveContribution'
}

PERCENT_SUCCESS_DATA_FIELDS = {
    'shootingPercentageHighTeleop': {'teleop', 'shoot', 'innerPort', 'outerPort'},
    'shootingPercentageLowTeleop': {'teleop', 'shoot', 'lowerGoal'}
}


def get_team(team_number):
    homeDir = os.path.expanduser('~')
    teams = os.listdir(os.path.join(homeDir, 'MNDU2-2020Server/cache/teams'))
    return [json.loads(open(os.path.join(homeDir, 'MNDU2-2020Server/cache/teams/', team)).read()) for team in teams if team != '.DS_Store' and int(team.split('.')[0]) == int(team_number)][0]


def get_timds(team_number):
    homeDir = os.path.expanduser('~')
    TIMDs = [timd for timd in os.listdir(os.path.join(homeDir, 'MNDU2-2020Server/cache/TIMDs')) if timd != '.DS_Store']
    return [json.loads(open(os.path.join(homeDir, 'MNDU2-2020Server/cache/TIMDs/', TIMD)).read()) for TIMD in TIMDs if int(TIMD.split('-')[1]) == int(team_number)]


def calculate_team(team_number, last_timd, is_json=False):
    if is_json is not False:
        team = is_json
        timds = team['timds']

    else:
        try:
            team = get_team(team_number)
            timds = get_timds(team_number)
        except IndexError:
            team = {'teamNumber': last_timd['team_number']}
            timds = [last_timd]

        team['timds'] = sorted(timds, key=lambda timd: timd['header']['matchNumber'])

    num_matches = len(timds)
    num_no_shows = len([timd for timd in timds if timd['header']['noShow']])

    timds = [timd for timd in timds if not timd['header']['noShow']]

    l3m_timds = sorted(timds, key=lambda timd: timd['header']['matchNumber'])[-3:]

    totals = {'cellsScoredHigh': stats.total_filter_values(stats.filter_timeline_actions(timds, actionType='shoot', actionTime='teleop'), 'outerPort', 'innerPort'),
              'cellsScoredLow': stats.total_filter_values(stats.filter_timeline_actions(timds, actionType='shoot', actionTime='teleop'), 'lowerGoal'),
              'timeDefending': sum([timd['calculated']['timeDefending'] for timd in timds]),
              'timeIncap': sum([timd['calculated']['timeIncap'] for timd in timds])}

    team_abilities = {}
    team_abilities['shootCellsHigh'] = True if totals['cellsScoredHighTeleop'] > 0  else False
    team_abilities['shootCellsLow'] = True if totals['cellsScoredLowTeleop'] > 0 else False
    team_abilities['climb'] = True if len(stats.filter_timeline_actions(timds, actionType='climb', climbHeight='hanging')) > 0 else False
    team_abilities['wheelSpunInMatch'] = True if len(stats.filter_timeline_actions(timds, actionType='wheel')) > 0 else False
    team_abilities['moveOffLineAuto'] = True if len([timd for timd in timds if timd['header']['leftLine']]) > 0 else False
    team['team_abilities'] = team_abilities

    for average_data_field, timd_data_field in TOTAL_AVERAGE_DATA_FIELDS.items():
        totals[average_data_field] = stats.avg([timd['calculated'].get(timd_data_field) for timd in timds])
    team['totals'] = totals

    l3ms = {}
    for l3m_average_data_field, timd_data_field in L3M_AVERAGE_DATA_FIELDS.items():
        l3ms[l3m_average_data_field] = stats.avg([timd['calculated'].get(timd_data_field) for timd in l3m_timds])
    team['l3ms'] = l3ms

    p75s = {}
    for p75_data_field, timd_data_field in P75_DATA_FIELDS.items():
        p75s[p75_data_field] = stats.p75([timd['calculated'].get(timd_data_field) for timd in timds])
    team['p75s'] = p75s

    SDs = {}
    for SD_data_field, timd_data_field in SD_DATA_FIELDS.items():
        SDs[SD_data_field] = stats.SD([timd['calculated'].get(timd_data_field) for timd in timds])
    team['SDs'] = SDs

    maxes = {}
    for max_data_field, timd_data_field in MAX_DATA_FIELDS.items():
        maxes[max_data_field] = stats.maximum([timd['calculated'].get(timd_data_field) for timd in timds])
    team['maxes'] = maxes

    percentages = {}
    for success_data_field, filters in PERCENT_SUCCESS_DATA_FIELDS.items():
        percentages[success_data_field] = stats.percent_success_shooting(timds, 'teleop', 'shoot', *filters)

    percentages['leftInitLine'] = round(100 * (len([timd for timd in timds if timd['header']['leftLine']]) / len(timds))) if len(timds) is not 0 else 0

    percentages['climbSuccessRate'] = round(100 * (len(stats.filter_timeline_actions(timds, actionType='climb', climbHeight='hanging')) / len(stats.filter_timeline_actions(timds, actionType='climb', climbHeight='fell')))) if len(stats.filter_timeline_actions(timds, actionType='climb', climbHeight='hanging')) != 0 else None
    percentages['levelClimbPercentage'] = round(100 * (len(stats.filter_timeline_actions(timds, actionType='climb', levelClimb=True)) / len(stats.filter_timeline_actions(timds, actionType='climb', climbHeight='hanging')))) if len(stats.filter_timeline_actions(timds, actionType='climb', climbHeight='hanging')) != 0 else None
    percentages['parkPercentage'] = round(100 * (len(stats.filter_timeline_actions(timds, actionType='climb', climbHeight='parked')) / len(timds))) if len(timds) is not 0 else 0
    percentages['climbPercentage'] = round(100 * (len(stats.filter_timeline_actions(timds, actionType='climb', climbHeight='hanging')) / len(timds))) if len(timds) is not 0 else 0

    percentages['percentOfTotalTeleopDefending'] = round(100 * (team['totals']['timeDefending'] / (len(timds) * 135))) if len(timds) is not 0 else 0

    percentages['percentOfTimeIncap'] = round(100 * (team['totals']['timeIncap'] / (len(timds) * 150))) if len(timds) is not 0 else 0

    percentages['percentOfMatchesNoShow'] = round(100 * (num_no_shows / num_matches + num_no_shows))

    team['percentages'] = percentages

    # team['rankings'] = calculations.calculateRankings.calculate_rankings(int(team_number), team)

    print(f'{team_number} calculated')

    homeDir = os.path.expanduser('~')

    pyrebase_config = {
        "apiKey": sensitiveInfo.firebase_api_key(),
        "authDomain": "mndu2-2020.firebaseapp.com",
        "databaseURL": "https://mndu2-2020.firebaseio.com",
        "storageBucket": "mndu2-2020.appspot.com"
    }

    if is_json is False:
        firebase = pyrebase.initialize_app(pyrebase_config)
        database = firebase.database()

        # Save data in local cache
        if not os.path.exists(os.path.join(homeDir, 'MNDU2-2020Server/cache/teams')):
            os.makedirs(os.path.join(homeDir, 'MNDU2-2020Server/cache/teams'))

        with open(os.path.join(homeDir, f'MNDU2-2020Server/cache/teams/{team_number}.json'), 'w') as file:
            json.dump(team, file)
        print(f'{team_number} cached')

        database.child("teams").child(team_number).set(team)
        print(f'{team_number} uploaded to Firebase\n')

    return team
