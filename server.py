import sensitiveInfo
from calculations import calculateTIMD, calculateTeam
import export
import os
import pyrebase
import time
import slack

homeDir = os.path.expanduser('~')

pyrebase_config = {
        "apiKey": sensitiveInfo.firebase_api_key(),
        "authDomain": "mndu2-2020.firebaseapp.com",
        "databaseURL": "https://mndu2-2020.firebaseio.com",
        "storageBucket": "mndu2-2020.appspot.com"
    }

firebase = pyrebase.initialize_app(pyrebase_config)
database = firebase.database()


def reset_timds():
    for timd in database.child('decompedTIMDs').get().each():
        database.child("rawTIMDs").child(timd.key()).set(timd.val())
        database.child("decompedTIMDs").child(timd.key()).remove()


def get_num_timds_for_match(match_number):
    homeDir = os.path.expanduser('~')
    timds = os.listdir(os.path.join(homeDir, 'MNDU2-2020Server/cache/TIMDs'))
    return len([timd for timd in timds if timd.split('-')[0] == match_number])


def run_server_testing():

    rawTIMDs = database.child('rawTIMDs').get()
    if rawTIMDs.val() is None:
        reset_timds()

    rawTIMDs = database.child('rawTIMDs').get()
    for temp_timd in rawTIMDs.each():
        timd = calculateTIMD.calculate_timd(temp_timd.val(), temp_timd.key())
        database.child("rawTIMDs").child(temp_timd.key()).remove()
        team_num = temp_timd.key().split("-")[1]
        calculateTeam.calculate_team(team_num, timd)

    print("calced, exporting")
    export.export_spreadsheet()


def run_server_comp():
    slack_token = sensitiveInfo.slack_api_key()
    slack_client = slack.WebClient(token=slack_token)

    current_unfinished_match = int(input("Next Match to be played?\n"))
    timds_in_last_match = 0

    while True:
        rawTIMDs = database.child('rawTIMDs').get()
        if rawTIMDs.val() is None:
            time.sleep(5)
        else:
            for temp_timd in rawTIMDs.each():
                timd = calculateTIMD.calculate_timd(temp_timd.val(), temp_timd.key())

                match_num = timd['match_number']
                if match_num == current_unfinished_match:
                    timds_in_last_match += 1
                    if timds_in_last_match == 6:
                        print("\nAll TIMDs for QM " + str(current_unfinished_match) + " synced\n")
                        timds_in_last_match = 0

                        team_num = temp_timd.key().split("-")[1]
                        calculateTeam.calculate_team(team_num, timd)

                        #export.export_spreadsheet()
                        #print("Data exported")
                        #export.upload_to_drive(" Post QM" + str(current_unfinished_match) + "Full Export")
                        #print("Data uploaded to Drive\n")
                        slack_client.chat_postMessage(
                            channel="U7EA0HCJW",
                            text="All TIMDs for Match " + str(current_unfinished_match) + "processed" # and data exported"
                        )
                        current_unfinished_match += 1

                elif match_num > current_unfinished_match:
                    print("WARNING: MISSING TIMD FOR MATCH " + str(current_unfinished_match))
                    slack_client.chat_postMessage(
                        channel="U7EA0HCJW",
                        text="WARNING: TIMD for Match " + str(match_num) + " uploaded before Match " +
                             str(current_unfinished_match) + " had 6 TIMDs!"
                    )
                    current_unfinished_match += 1
                    timds_in_last_match = 1

                elif match_num < current_unfinished_match:
                    print("WARNING: CALCULATING TIMD FROM PAST MATCH " + str(current_unfinished_match - 1))
                    if get_num_timds_for_match("QM" + str(match_num)) == 6:
                        print("\nAll TIMDs for QM " + str(match_num) + " synced\n")
                        timds_in_last_match = 0
                        export.export_spreadsheet()
                        print("Data exported")
                        export.upload_to_drive(" Post QM" + str(match_num) + "Full Export")
                        print("Data uploaded to Drive\n")
                        slack_client.chat_postMessage(
                            channel="U7EA0HCJW",
                            text="All TIMDs for Match " + str(match_num) + "processed and data exported"
                        )
                    elif get_num_timds_for_match("QM" + str(match_num)) > 6:
                        print("WARNING: More than 6 TIMDs for Match " + str(match_num) + " processed!")
                        # TODO Delete the extra one
                    else:
                        print("WARNING: Still missing " + str(6 - get_num_timds_for_match("QM" + str(match_num))) + " TIMDs for Match " + str(match_num))

                database.child("rawTIMDs").child(temp_timd.key()).remove()
                team_num = temp_timd.key().split("-")[1]
                calculateTeam.calculate_team(team_num, timd)


if __name__ == "__main__":
    run_server_testing()
