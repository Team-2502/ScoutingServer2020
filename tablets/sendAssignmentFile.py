
"""
Shamelessly stolen almost verbatim from 1678
Copyright (c) 2019 FRC Team 1678: Citrus Circuits

Sends assignment file to scout tablets over ADB.

Verifies that the filehv vh cgh fctf is successfully transfered.
ADB stands for Android Debug Bridge."""
# External imports
import subprocess
import time

# Serial number to human-readable device name
DEVICE_NAMES = {
    'G000L40763270NAL': 'Scout 1',
    'G000L40763270V9A': 'Scout 2',
    'G000L40763270WH5': 'RED 3',
    'G000L40763270QKL': 'BLUE 1',
    'G000L40763270NX9': 'BLUE 2',
    'G000L40763270WLQ': 'BLUE 3',
    'G000L40763270R0J': 'RED 2'
}

ASSIGNMENT_FILE_PATH = '/Users/64013459//MMR-2019Server/assignments/BackupAssignments.txt'

# List of devices to which 'assignments.txt' has already been sent
DEVICES_WITH_FILE = []

def validate_file(device_id):
    """Validates that the assignment file was successfully transfered.

    Compares the assignments.txt on the tablet to the locally stored
    assignments.txt file.

    device_id is the serial number of the device"""
    # Reads the server version of assignments.txt
    with open(ASSIGNMENT_FILE_PATH, 'r') as file:
        computer_data = file.read()
    # Reads the assignments.txt file on the tablet
    # The ADB -s flag specifies a device using its serial number
    tablet_data = subprocess.check_output(
        f'adb -s {device_id} shell cat /mnt/sdcard/Scouting2020/assignments.txt',
        shell=True)
    # 'tablet_data' is a byte-like string and needs to be decoded
    tablet_data = tablet_data.decode('utf-8')
    # Replaces '\r\n' with '\n' to match the UNIX format for newlines
    tablet_data = tablet_data.replace('\r\n', '\n')
    return tablet_data == computer_data

while True:
    # Stores output from 'adb devices'
    # 'adb devices' returns the serial numbers of all devices connected
    # over ADB.
    # Example output of 'adb devices':
    # "List of devices attached\n015d2568753c1408\tdevice\n015d2856d607f015\tdevice"
    OUTPUT = subprocess.check_output('adb devices', shell=True)
    # 'OUTPUT' is a byte-like string and needs to be decoded
    OUTPUT = OUTPUT.decode('utf-8')
    # '.rstrip('\n')' removes trailing newlines
    # [1:] removes 'List of devices attached'
    OUTPUT = OUTPUT.rstrip('\n').split('\n')[1:]
    # Remove '\tdevice' from each line
    DEVICES = [line.split('\t')[0] for line in OUTPUT]
    #print(DEVICES)

    # Wait for USB connection to initialize
    time.sleep(.1)  # .1 seconds

    for device in DEVICES:
        if device not in DEVICES_WITH_FILE:
            # Calls 'adb push' command, which uses the Android Debug
            # Bridge (ADB) to copy the assignment file to the tablet.
            # The -s flag specifies the device by its serial number.
            subprocess.call(
                f"adb -s {device} push '{ASSIGNMENT_FILE_PATH}' '/mnt/sdcard/Scouting2020/assignments.txt'",
                shell=True)

            if validate_file(device) is True:
                DEVICES_WITH_FILE.append(device)
                # Convert serial number to human-readable name
                # Example: '00a2849de' becomes 'Scout 7'
                device_name = DEVICE_NAMES[device]
                print(f'Loaded assignment file onto {device_name} tablet.')
