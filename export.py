import pygsheets
import pyrebase
import os
import ast


def export_spreadsheet():
    client = pygsheets.authorize(service_account_env_var="g_drive_creds")

    wb = client.open('Scouting Template 2021')
    team_export = wb.worksheet_by_title("Test Team Export")
    timd_export = wb.worksheet_by_title("Test TIMD Export")
    team_export.clear()
    timd_export.clear()

    try:
        scout_export = wb.worksheet_by_title("Scout Data Export")
        scout_export.clear()
    except pygsheets.WorksheetNotFound:
        scout_export = wb.add_worksheet("Scout Data Export")

    scout_amounts = {}

    firebase = pyrebase.initialize_app(ast.literal_eval(os.environ['firebase_info']))
    database = firebase.database()

    teams = database.child("teams").get().each()
    team1 = teams[0].val()

    totals = ([key for key in team1['totals'].keys()], 'totals')
    l3ms = ([key for key in team1['l3ms'].keys()], 'l3ms')
    SDs = ([key for key in team1['SDs'].keys()], 'SDs')
    maxes = ([key for key in team1['maxes'].keys()], 'maxes')
    team_abilities = ([key for key in team1['team_abilities'].keys()], 'team_abilities')
    percentages = ([key for key in team1['percentages'].keys()], 'percentages')
    p75s = ([key for key in team1['p75s'].keys()], 'p75s')
    # sykes = ([key for key in team1['sykes'].keys()], 'sykes')

    timdHeader = ([key for key in team1['timds'][0]['header'].keys()], 'header')
    climb = ([key for key in team1['timds'][0]['climb'].keys()], 'climb')
    calculated = ([key for key in team1['timds'][0]['calculated'].keys()], 'calculated')

    headers = [totals, l3ms, SDs, maxes, team_abilities, percentages, p75s]  # [sykes]
    timdHeaders = [timdHeader, calculated, climb]

    all_team_headers = ['Number'] + [item for elem in [header[0] for header in headers] for item in elem]
    all_timd_headers = ['Team', 'Match'] + [item for elem in [header[0] for header in timdHeaders] for item in elem]

    team_export_values = [all_team_headers]
    timd_export_values = [all_timd_headers]

    for team in teams:
        team = team.val()
        team_values = [team['teamNumber']]

        for header in headers:
            for key in header[0]:
                team_values.append(team[header[1]][key])
        team_export_values.append(team_values)

        for timd in team['timds']:
            timd_values = [timd['team_number'], timd['match_number']]

            scout = timd['header']['scoutKey']

            if scout not in scout_amounts.keys():
                scout_amounts[scout] = 1
            else:
                scout_amounts[scout] += 1

            if timd['header']['noShow']:
                for key in timdHeader[0]:
                    timd_values.append(timd['header'][key])

            else:
                for header in timdHeaders:
                    for key in header[0]:
                        timd_component_header = timd[header[1]]
                        if key in timd_component_header.keys():
                            timd_values.append(timd_component_header[key])

            timd_export_values.append(timd_values)

    team_export.insert_rows(0, values=team_export_values)
    timd_export.insert_rows(0, values=timd_export_values)
    scout_export.insert_cols(0, values=[list(scout_amounts.keys()), list(scout_amounts.values())])


if __name__ == '__main__':
    export_spreadsheet()
