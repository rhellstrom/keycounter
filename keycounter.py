import subprocess
import struct
import json
import datetime
from threading import Thread, Lock
from time import sleep

from typing import Dict
from args import parse_args 


class MultipleEventFilesError(Exception):
    pass

# From the output of /proc/bus/input/devices we can determine what eventfile
# is used for the keyboard. EV value should always be 120013
# Mice can also show up as a keyboard so until we figure out another way to filter
# output we return error if more than one file is found
def get_keyboard_device_filename() -> str: 
    command_str = "grep -E 'Handlers|EV' /proc/bus/input/devices | grep -B1 120013 | grep -Eo 'event[0-9]+'"
    res = subprocess.run(['sh', '-c', command_str], capture_output=True, text=True)
    event_file = res.stdout.strip()
    # Check string for newline, if present there are more than one eventfile matching description
    if "\n" in event_file:
        raise MultipleEventFilesError("Multiple event files found. Please specify event file as an argument.")
    return f"/dev/input/{event_file}" 

def write_to_file(filename: str, keys_dict: Dict[int, int], interval: int, lock: Lock) -> None:
    while True:
            lock.acquire()
            print("DEBUG")
            with open(filename, "w") as file:
               json.dump(keys_dict, file)
            lock.release()
            sleep(interval)
# TODO: Gracefully exit write_to_file on KeyboardInterrupt and other events
# TODO: Name output file after time and date of program execution i.e session
# TODO: Create a dir to store our session output in?
def main() -> None:
    now = datetime.datetime.now()
    print(now)

    lock = Lock()
    args = parse_args()
    interval = args.write_interval
    keys = args.keys

    # Hold the keys and their count in a dict
    keys_dict = {key: 0 for key in keys}

    if args.event_file:
       device_file_path = args.event_file 
    else:
        try: 
            device_file_path = get_keyboard_device_filename()
        except MultipleEventFilesError as e:
            print(e)
            exit(1)

    write_thread = Thread(target=write_to_file, args=("output", keys_dict, interval, lock))
    # Setting daemon to True kills the thread when main is killed.
    # If files are open or not is not taken into consideration...
    write_thread.daemon = True
    write_thread.start()

    # Open the event file in read-binary mode
    device_file = open(device_file_path, "rb")

    while True:
        # kernel.org/doc/Documentation/input/input.txt
        # one entry is 24 bytes
        data = device_file.read(24);
        unpacked_data = struct.unpack('4IHHI', data)
    
        # Key code represent the key pressed
        # Key value if the is pressed or released. Act on press.
        key_code = unpacked_data[5]
        key_value = unpacked_data[6]
        if key_value == 1 and key_code in keys:
            lock.acquire()
            keys_dict[key_code] += 1
            print(keys_dict) 
            lock.release()

if __name__ == "__main__":
    main()
