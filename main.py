import struct
import json
import datetime
from threading import Thread, Lock
from time import sleep

from typing import Dict

from keyboard_utils import get_keyboard_device_filename
from args import parse_args 


def write_to_file(filename: str, keys_dict: Dict[int, int], interval: int, lock: Lock) -> None:
    while True:
            lock.acquire()
            print("DEBUG")
            with open(filename, "w") as file:
               json.dump(keys_dict, file)
            lock.release()
            sleep(interval)

def output_filename(filename: str = "") -> str:
    if filename:
        return filename
    else:
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d--%H:%M")

# TODO: Gracefully exit write_to_file on KeyboardInterrupt and other events
# TODO: Create a dir to store our session output in?
def main() -> None:
    lock = Lock()
    args = parse_args()

    keys = args.keys
    output_file = output_filename(args.output_file)

    # Hold the keys and their count in a dict
    keys_dict = {key: 0 for key in keys}

    write_thread = Thread(target=write_to_file, args=(output_file, keys_dict, args.write_interval, lock))
    # Setting daemon to True kills the thread when main is killed.
    # If files are open or not is not taken into consideration...
    write_thread.daemon = True
    write_thread.start()

    device_file_path = get_keyboard_device_filename(args.event_file)
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
