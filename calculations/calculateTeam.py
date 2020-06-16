import pyrebase

import sensitiveInfo
from utils import *
from calculations import calculateTIMD

TOTAL_AVERAGE_DATA_FIELDS = {
    'avgCellsScoredTele': 'cellsScoredTeleop',
    'avgCellsScoredAuto': 'cellsScoredAuto',
    'avgCellsScoredHigh': 'cellsScoredHighTeleop',
    'avgCellsScoredLow': 'cellsScoredLowTeleop',
    'avgCellsScoredTrench': 'cellsScoredTrenchTeleop',
    'avgCellsScoredField':'cellsScoredMiddleFieldTeleop',
    'avgTimeIncap': 'timeIncap',
    'avgTimeDefending': 'timeDefending',
    'avgTOC': 'trueOffensiveContribution',
    'avgCycles': 'totalCycles'
}

L3M_AVERAGE_DATA_FIELDS = {
    'l3mAvgCellsScored': 'cellsScoredTeleop',
    'l3mAvgCellsScoredHigh': 'cellsScoredHighTeleop',
    'l3mAvgCellsScoredLow': 'cellsScoredLowTeleop',
    'l3mAvgTimeIncap': 'timeIncap',
    'l3mAvgTimeDefending': 'timeDefending'
}

P75_DATA_FIELDS = {
    'p75CellsScored': 'cellsScoredTeleop',
    'p75CellsScoredHigh': 'cellsScoredHighTeleop',
    'p75CellsScoredLow': 'cellsScoredLowTeleop',
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
    'shootingPercentageHighTeleop': {'innerPort', 'outerPort'}
}


# If testing last_timd is actually a list of all timds that make up the team, otherwise just the last timd
def calculate_team(team_number, last_timd, test=False):
    firebase = pyrebase.initialize_app(sensitiveInfo.firebase_info_dev_2021())
    database = firebase.database()

    if test is not False:
        timds = [calculateTIMD.calculate_timd(timd, "test", True) for timd in last_timd]
        team = {'teamNumber': team_number, 'timds': sorted(timds, key=lambda timd: timd['header']['matchNumber'])}
    else:
        team = database.child('teams').child(team_number).get().val()
        if team is None:
            team = {'teamNumber': last_timd['team_number']}
            timds = [last_timd]
        else:
            timds = team['timds']

        team['timds'] = sorted(timds, key=lambda timd: timd['header']['matchNumber'])

    num_matches = len(timds)
    num_no_shows = len([timd for timd in timds if timd['header']['noShow']])

    timds = [timd for timd in timds if not timd['header']['noShow']]

    l3m_timds = sorted(timds, key=lambda timd: timd['header']['matchNumber'])[-3:]

    totals = {'cellsScoredHighTeleop': stats.total_filter_values(stats.filter_timeline_actions(timds, actionType='shoot', actionTime='teleop'), 'outerPort', 'innerPort'),
              'cellsScoredLowTeleop': stats.total_filter_values(stats.filter_timeline_actions(timds, actionType='shoot', actionTime='teleop'), 'lowerGoal'),
              'timeDefending': sum([timd['calculated']['timeDefending'] for timd in timds]),
              'timeIncap': sum([timd['calculated']['timeIncap'] for timd in timds])}

    for average_data_field, timd_data_field in TOTAL_AVERAGE_DATA_FIELDS.items():
        totals[average_data_field] = stats.avg([timd['calculated'].get(timd_data_field) for timd in timds])

    totals['avgTotalCellsScored'] = totals['avgCellsScoredTele'] + totals['avgCellsScoredAuto']
    team['totals'] = totals

    team_abilities = {}
    team_abilities['shootCellsHigh'] = True if totals['cellsScoredHighTeleop'] > 0  else False
    team_abilities['shootCellsLow'] = True if totals['cellsScoredLowTeleop'] > 0 else False
    team_abilities['climb'] = True if len(stats.filter_timeline_actions(timds, actionType='climb', climbHeight='hanging')) > 0 else False
    team_abilities['wheelSpunInMatch'] = True if len(stats.filter_timeline_actions(timds, actionType='wheel')) > 0 else False
    team_abilities['moveOffLineAuto'] = True if len([timd for timd in timds if timd['header']['leftLine']]) > 0 else False
    team['team_abilities'] = team_abilities

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

    percentages['climbSuccessRate'] = round(100 * (len(stats.filter_timeline_actions(timds, actionType='climb', climbHeight='hanging')) / (len(stats.filter_timeline_actions(timds, actionType='climb', climbHeight='fell')) + len(stats.filter_timeline_actions(timds, actionType='climb', climbHeight='hanging'))))) if len(stats.filter_timeline_actions(timds, actionType='climb', climbHeight='hanging')) != 0 else 0
    percentages['levelClimbPercentage'] = round(100 * (len(stats.filter_timeline_actions(timds, actionType='climb', levelClimb=True)) / len(stats.filter_timeline_actions(timds, actionType='climb', climbHeight='hanging')))) if len(stats.filter_timeline_actions(timds, actionType='climb', climbHeight='hanging')) != 0 else 0
    percentages['parkPercentage'] = round(100 * (len(stats.filter_timeline_actions(timds, actionType='climb', climbHeight='parked')) / len(timds))) if len(timds) is not 0 else 0
    percentages['climbPercentage'] = round(100 * (len(stats.filter_timeline_actions(timds, actionType='climb', climbHeight='hanging')) / len(timds))) if len(timds) is not 0 else 0

    percentages['percentOfTotalTeleopDefending'] = round(100 * (team['totals']['timeDefending'] / (len(timds) * 135))) if len(timds) is not 0 else 0

    percentages['percentOfTimeIncap'] = round(100 * (team['totals']['timeIncap'] / (len(timds) * 135))) if len(timds) is not 0 else 0

    percentages['percentOfTimeOffense'] = (100 - percentages['percentOfTotalTeleopDefending'] - percentages['percentOfTimeIncap'])

    percentages['percentOfMatchesNoShow'] = round(100 * (num_no_shows / num_matches))

    team['percentages'] = percentages

    # team['rankings'] = calculations.calculateRankings.calculate_rankings(int(team_number), team)

    if test is not False:
        database.child("teams").child("test").set(team)

    else:
        print(f'{team_number} calculated')

        database.child("teams").child(team_number).set(team)
        print(f'{team_number} uploaded to Firebase\n')

    return team
