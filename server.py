from calculations import calculateTIMD, calculateTeam
import export
import pyrebase
import time
import slack
import ast
import os


def reset_timds(database):
    for timd in database.child('decompedTIMDs').get().each():
        database.child("rawTIMDs").child(timd.key()).set(timd.val())
        database.child("decompedTIMDs").child(timd.key()).remove()


def get_num_timds_for_match(match_number, database):
    timds = database.child("TIMDs").get().each()
    return len([timd for timd in timds if timd.val()['match_number'] == match_number])


def run_server_testing():
    firebase = pyrebase.initialize_app(ast.literal_eval(os.environ['firebase_info']))
    database = firebase.database()

    rawTIMDs = database.child('rawTIMDs').get()
    if rawTIMDs.val() is None:
        reset_timds(database)

    rawTIMDs = database.child('rawTIMDs').get()
    for temp_timd in rawTIMDs.each():
        timd = calculateTIMD.calculate_timd(temp_timd.val(), temp_timd.key())
        database.child("rawTIMDs").child(temp_timd.key()).remove()
        team_num = temp_timd.key().split("-")[1]
        calculateTeam.calculate_team(team_num, timd)

    print("calced, exporting test")
    export.export_spreadsheet()


def run_server():
    firebase = pyrebase.initialize_app(ast.literal_eval(os.environ['firebase_info']))
    database = firebase.database()

    slack_token = os.environ['slack_api_key']
    slack_client = slack.WebClient(token=slack_token)
    slack_channel = os.environ['head_scout_slack_id']

    timds_for_current_match = 0

    while True:
        rawTIMDs = database.child('rawTIMDs').get()

        if rawTIMDs.val() is None:
            time.sleep(10)

        else:
            try:
                current_unscouted_match = database.child('config').child('currentMatch').get().val()

                for temp_timd in rawTIMDs.each():

                    timd = calculateTIMD.calculate_timd(temp_timd.val(), temp_timd.key())
                    database.child("rawTIMDs").child(temp_timd.key()).remove()
                    team_num = temp_timd.key().split("-")[1]
                    calculateTeam.calculate_team(team_num, timd)

                    match_num = timd['match_number']
                    if match_num == current_unscouted_match:
                        timds_for_current_match += 1
                        if timds_for_current_match == 6:
                            print("\nAll TIMDs for QM " + str(current_unscouted_match) + " synced\n")
                            timds_for_current_match = 0

                            export.export_spreadsheet()
                            print("Data exported")
                            slack_client.chat_postMessage(
                                channel=slack_channel,
                                text="All TIMDs for Match " + str(current_unscouted_match) + " processed and data exported"
                            )
                            database.child('config').child('currentMatch').set(current_unscouted_match + 1)

                    elif match_num > current_unscouted_match:
                        print("WARNING: MISSING TIMD FOR MATCH " + str(current_unscouted_match))
                        slack_client.chat_postMessage(
                            channel=slack_channel,
                            text="WARNING: TIMD for Match " + str(match_num) + " uploaded before Match " +
                                 str(current_unscouted_match) + " had 6 TIMDs!"
                        )
                        database.child('config').child('currentMatch').set(match_num)
                        timds_for_current_match = 1

                    elif match_num < current_unscouted_match:
                        print("WARNING: CALCULATING TIMD FROM PAST MATCH " + str(match_num))
                        if get_num_timds_for_match(match_num, database) == 6:
                            print("\nAll TIMDs for QM " + str(match_num) + " synced\n")
                            timds_for_current_match = 0
                            export.export_spreadsheet()
                            print("Data exported")
                            slack_client.chat_postMessage(
                                channel=slack_channel,
                                text="All TIMDs for Match " + str(match_num) + "processed and data exported"
                            )
                        elif get_num_timds_for_match(match_num, database) > 6:
                            slack_client.chat_postMessage(
                                channel=slack_channel,
                                text="More than 6 TIMDs processed for Match " + str(match_num)
                            )
                        else:
                            print("WARNING: Still missing " + str(6 - get_num_timds_for_match(match_num, database)) + " TIMDs for Match " + str(match_num))
            except Exception as e:
                slack_client.chat_postMessage(
                    channel=slack_channel,
                    text="Exception occurred: " + str(e)
                )
                exit()


if __name__ == "__main__":
    run_server()
