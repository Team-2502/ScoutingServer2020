import sensitiveInfo

import json
import os
import pyrebase

from utils import *
from utils.stats import filter_timeline_actions, total_filter_values, percent_success_shooting


def calculate_statistics(decompressed_timd):
    calculated_data = {}
    shots_teleop = filter_timeline_actions([decompressed_timd], actionType='shoot', actionTime='teleop')
    print(decompressed_timd)
    print(shots_teleop)
    shots_teleop_middle_of_field = [shot for shot in shots_teleop if shot not in (filter_timeline_actions([decompressed_timd], actionType='shoot', actionTime='teleop', actionPlace='trenchRun') + filter_timeline_actions([decompressed_timd], actionType='shoot', actionTime='teleop', actionPlace='targetZone'))]
    shots_auto = filter_timeline_actions([decompressed_timd], actionType='shoot', actionTime='auto')

    calculated_data['cellsScoredTeleop'] = total_filter_values(shots_teleop, 'totalShotsMade')
    calculated_data['cellsScoredHighTeleop'] = total_filter_values(shots_teleop, 'outerPort', 'innerPort')
    calculated_data['cellsScoredLowTeleop'] = total_filter_values(shots_teleop, 'lowerGoal')
    calculated_data['cellsScoredTrenchTeleop'] = total_filter_values(filter_timeline_actions(shots_teleop, actionPlace='trenchRun'), 'totalShotsMade')
    calculated_data['cellsScoredTargetZoneTeleop'] = total_filter_values(filter_timeline_actions(shots_teleop, actionPlace='targetZone'), 'totalShotsMade')
    calculated_data['cellsScoredMiddleFieldTeleop'] = total_filter_values(shots_teleop_middle_of_field, "totalShotsMade")
    calculated_data['cellsScoredAuto'] = total_filter_values(shots_auto, 'totalShotsMade')
    calculated_data['cellsScoredAutoHigh'] = total_filter_values(shots_auto, 'outerPort', 'innerPort')
    calculated_data['cellsScoredAutoLow'] = total_filter_values(shots_auto, 'lowerGoal')
    calculated_data['cellsShotAuto'] = total_filter_values(shots_auto, 'totalShotsMade', 'misses')
    calculated_data['cellsShotTeleop'] = total_filter_values(shots_teleop, 'totalShotsMade', 'misses')
    calculated_data['cellsMissedAuto'] = total_filter_values(shots_auto, 'misses')
    calculated_data['cellsMissedTeleop'] = total_filter_values(shots_teleop, 'misses')

    calculated_data['totalCycles'] = len(shots_teleop)
    calculated_data['totalCyclesTrench'] = len(filter_timeline_actions([decompressed_timd], actionType='shoot', actionTime='teleop', actionPlace='trenchRun'))
    calculated_data['totalCyclesTargetZone'] = len(filter_timeline_actions([decompressed_timd], actionType='shoot', actionTime='teleop', actionPlace='targetZone'))
    calculated_data['totalCyclesField'] = len(shots_teleop_middle_of_field)

    calculated_data['shootingPercentageLowTeleop'] = percent_success_shooting([decompressed_timd], 'teleop', 'shoot', 'lowerGoal')
    calculated_data['shootingPercentageHighTeleop'] = percent_success_shooting([decompressed_timd], 'teleop', 'shoot', 'innerPort', 'outerPort')

    calculated_data['shootingPercentageLowAuto'] = percent_success_shooting([decompressed_timd], 'auto', 'shoot','lowerGoal')
    calculated_data['shootingPercentageHighAuto'] = percent_success_shooting([decompressed_timd], 'auto', 'shoot','innerPort', 'outerPort')

    calculated_data['timeDefending'] = total_filter_values(filter_timeline_actions([decompressed_timd], actionType='defense'), 'actionTime')
    calculated_data['timeIncap'] = total_filter_values(filter_timeline_actions([decompressed_timd], actionType='incap'), 'actionTime')

    calculated_data['trueOffensiveContribution'] = stats.true_offensive_contribution(decompressed_timd)

    return calculated_data


def calculate_climb(decompressed_timd):
    climb_action = filter_timeline_actions([decompressed_timd], actionType='climb')[0]
    return climb_action


def calculate_timd(compressed_timd, timd_name, test=False):
    decompressed_timd = decompression.decompress_timd(compressed_timd)
    if decompressed_timd['header']['noShow']:
        pass
    else:
        decompressed_timd['calculated'] = calculate_statistics(decompressed_timd)
        decompressed_timd['climb'] = calculate_climb(decompressed_timd)

    if not test:
        print(f'{timd_name} decompressed')

        homeDir = os.path.expanduser('~')

        pyrebase_config = {
            "apiKey": sensitiveInfo.firebase_api_key(),
            "authDomain": "mndu2-2020.firebaseapp.com",
            "databaseURL": "https://mndu2-2020.firebaseio.com",
            "storageBucket": "mndu2-2020.appspot.com"
        }

        firebase = pyrebase.initialize_app(pyrebase_config)
        database = firebase.database()

        # Save data in local cache
        if not os.path.exists(os.path.join(homeDir, 'MNDU2-2020Server/cache/TIMDs')):
            os.makedirs(os.path.join(homeDir, 'MNDU2-2020Server/cache/TIMDs'))

        with open(os.path.join(homeDir, f'MNDU2-2020Server/cache/TIMDs/{timd_name}.json'), 'w') as file:
            json.dump(decompressed_timd, file)
        print(f'{timd_name} cached')

        database.child("TIMDs").child(timd_name).set(decompressed_timd)
        database.child("decompedTIMDs").child(timd_name).set(compressed_timd)
        print(f'{timd_name} uploaded to Firebase\n')

    return decompressed_timd
