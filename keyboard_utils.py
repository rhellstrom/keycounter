import subprocess

class MultipleEventFilesError(Exception):
    pass

# From the output of /proc/bus/input/devices we can determine what eventfile
# is used for the keyboard. EV value should always be 120013
# Mice can also show up as a keyboard so until we figure out another way to filter
# output we return error if more than one file is found
def get_keyboard_device_filename(args_event_file: str = "") -> str: 
    if args_event_file:
        device_file_path = args_event_file
    else:
        try:
            command_str = "grep -E 'Handlers|EV' /proc/bus/input/devices | grep -B1 120013 | grep -Eo 'event[0-9]+'"
            res = subprocess.run(['sh', '-c', command_str], capture_output=True, text=True)
            event_file = res.stdout.strip()
            print(event_file)
            # Check string for newline, if present there are more than one eventfile matching description
            if "\n" in event_file:
                raise MultipleEventFilesError("Multiple event files found. Please specify event file as an argument.")
            device_file_path = f"/dev/input/{event_file}" 

        except MultipleEventFilesError as e:
            print(e)
            exit(1)

    return device_file_path
