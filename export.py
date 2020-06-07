import openpyxl
import json
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


def upload_to_drive(filename):
    gauth = GoogleAuth()
    # Try to load saved client credentials
    gauth.LoadCredentialsFile("oauthcreds.txt")

    if gauth.credentials is None:
        # Authenticate if they're not there

        # https://stackoverflow.com/a/55876179
        # This is what solved the issues:
        gauth.GetFlow()
        gauth.flow.params.update({'access_type': 'offline'})
        gauth.flow.params.update({'approval_prompt': 'force'})

        gauth.LocalWebserverAuth()

    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()

    else:
        # Initialize the saved creds
        gauth.Authorize()
    # Save the current credentials to a file
    gauth.SaveCredentialsFile("oauthcreds.txt")

    drive = GoogleDrive(gauth)

    # https://stackoverflow.com/a/22934892
    # https://stackoverflow.com/a/40236586
    drive_file = drive.CreateFile({'title': filename,
                                   "parents": [{"kind": "drive#fileLink", "id": "16HQEzd62UcJdDk5_yld39Ao9ncYffUKt"}]})

    # Read file and set it as a content of this instance.
    drive_file.SetContentFile("export.xlsx")
    drive_file.Upload()  # Upload the file.


def export_spreadsheet():
    homeDir = os.path.expanduser('~')
    teams = [json.loads(open(os.path.join(homeDir, 'MNDU2-2020Server/cache/teams/', team)).read()) for team in os.listdir(os.path.join(homeDir, 'MNDU2-2020Server/cache/teams')) if team != '.DS_Store']
    timds = [json.loads(open(os.path.join(homeDir, 'MNDU2-2020Server/cache/TIMDs/', timd)).read()) for timd in os.listdir(os.path.join(homeDir, 'MNDU2-2020Server/cache/TIMDs')) if timd != '.DS_Store']

    totals = ([key for key in teams[0]['totals'].keys()], 'totals')
    l3ms = ([key for key in teams[0]['l3ms'].keys()], 'l3ms')
    SDs = ([key for key in teams[0]['SDs'].keys()], 'SDs')
    maxes = ([key for key in teams[0]['maxes'].keys()], 'maxes')
    #rankings = ([key for key in teams[0]['rankings'].keys()], 'rankings')
    team_abilities = ([key for key in teams[0]['team_abilities'].keys()], 'team_abilities')
    percentages = ([key for key in teams[0]['percentages'].keys()], 'percentages')
    # sykes = ([key for key in teams[0]['sykes'].keys()], 'sykes')

    header = ([key for key in timds[0]['header'].keys()], 'header')
    climb = ([key for key in timds[0]['climb'].keys()], 'climb')
    calculated = ([key for key in timds[0]['calculated'].keys()], 'calculated')

    headers = [totals, l3ms, SDs, maxes, team_abilities, percentages]  # [sykes, rankings]
    timdHeaders = [header, calculated, climb]

    wb = openpyxl.load_workbook('export.xlsx')

    for sheet in wb.worksheets:
        wb.remove(sheet)

    raw_team_sheet = wb.create_sheet('Raw Teams Export')
    raw_team_sheet.cell(row=1, column=1).value = 'Number'

    raw_timd_sheet = wb.create_sheet('Raw TIMD Export')
    raw_timd_sheet.cell(row=1, column=1).value = 'Team'
    raw_timd_sheet.cell(row=1, column=2).value = 'Match'

    current_column = 3

    for header in timdHeaders:
        for key in header[0]:
            raw_timd_sheet.cell(row=1, column=current_column).value = key
            current_column += 1

    current_column = 2

    for header in headers:
        for key in header[0]:
            raw_team_sheet.cell(row=1, column=current_column).value = key
            current_column += 1

    current_timd_row = 2
    current_team_row = 2

    for team in teams:
        current_column = 2
        raw_team_sheet.cell(row=current_team_row, column=1).value = team['teamNumber']

        for header in headers:
            for key in header[0]:
                raw_team_sheet.cell(row=current_team_row, column=current_column).value = team[header[1]][key]
                current_column += 1

        current_team_row += 1

        for timd in team['timds']:
            current_column = 3
            raw_timd_sheet.cell(row=current_timd_row, column=1).value = timd['team_number']
            raw_timd_sheet.cell(row=current_timd_row, column=2).value = timd['match_number']

            for header in timdHeaders:
                for key in header[0]:
                    timd_component_header = timd[header[1]]
                    if key in timd_component_header.keys():
                        raw_timd_sheet.cell(row=current_timd_row, column=current_column).value = timd_component_header[key]
                    current_column += 1

            current_timd_row += 1

    wb.save('export.xlsx')


if __name__ == "__main__":
    export_spreadsheet()
