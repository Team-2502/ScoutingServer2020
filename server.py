import sensitiveInfo
from calculations import calculateTIMD, calculateTeam
import export
import pyrebase
import time
import slack


def reset_timds(database):
    for timd in database.child('decompedTIMDs').get().each():
        database.child("rawTIMDs").child(timd.key()).set(timd.val())
        database.child("decompedTIMDs").child(timd.key()).remove()


def get_num_timds_for_match(match_number, database):
    timds = database.child("TIMDs").get().each()
    return len([timd for timd in timds if timd.val()['match_number'] == match_number])


def run_server_testing():
    firebase = pyrebase.initialize_app(sensitiveInfo.firebase_info_dev_2021())
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


def run_server_comp():
    firebase = pyrebase.initialize_app(sensitiveInfo.firebase_info_dev_2021())
    database = firebase.database()

    slack_token = sensitiveInfo.slack_api_key()
    slack_client = slack.WebClient(token=slack_token)

    timds_for_current_match = 0

    while True:
        rawTIMDs = database.child('rawTIMDs').get()

        if rawTIMDs.val() is None:
            time.sleep(10)

        else:
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
                        export.upload_to_drive(" Post QM" + str(current_unscouted_match) + "Full Export")
                        print("Data uploaded to Drive\n")
                        slack_client.chat_postMessage(
                            channel="UC3TC3PN3",
                            text="All TIMDs for Match " + str(current_unscouted_match) + " processed and data exported"
                        )
                        database.child('config').child('currentMatch').set(current_unscouted_match + 1)

                elif match_num > current_unscouted_match:
                    print("WARNING: MISSING TIMD FOR MATCH " + str(current_unscouted_match))
                    slack_client.chat_postMessage(
                        channel="UC3TC3PN3",
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
                        export.upload_to_drive(" Post QM" + str(match_num) + "Full Export")
                        print("Data uploaded to Drive\n")
                        slack_client.chat_postMessage(
                            channel="UC3TC3PN3",
                            text="All TIMDs for Match " + str(match_num) + "processed and data exported"
                        )
                    elif get_num_timds_for_match(match_num, database) > 6:
                        slack_client.chat_postMessage(
                            channel="UC3TC3PN3",
                            text="More than 6 TIMDs processed for Match " + str(match_num)
                        )
                        # TODO Delete the extra one
                    else:
                        print("WARNING: Still missing " + str(6 - get_num_timds_for_match(match_num, database)) + " TIMDs for Match " + str(match_num))


if __name__ == "__main__":
    run_server_comp()
