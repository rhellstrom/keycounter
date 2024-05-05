import subprocess
import struct

# From the output of /proc/bus/input/devices we can determine what eventfile
# is used for the keyboard. EV value should always be 120013
def get_keyboard_device_filename(): 
    command_str = "grep -E 'Handlers|EV' /proc/bus/input/devices | grep -B1 120013 | grep -Eo 'event[0-9]+'"
    res = subprocess.run(['sh', '-c', command_str], capture_output=True, text=True)
    event_file = res.stdout.strip()
    return f"/dev/input/{event_file}" if event_file else None

counter = 0
device_file_path = get_keyboard_device_filename()
device_file = open(device_file_path, "rb")
while True:
    # kernel.org/doc/Documentation/input/input.txt
    # one entry is 24 bytes
    data = device_file.read(24);
    unpacked_data = struct.unpack('4IHHI', data)
    
    key_code = unpacked_data[5]
    key_value = unpacked_data[6]
   # print(unpacked_data)
    print("", key_code)
    if key_value == 1 and key_code in [26, 39, 40]:
       counter += 1
       print(counter)

