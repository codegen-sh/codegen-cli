import os


# TODO: move to shared print utils
def print_debug_message(message):
    if os.environ.get("DEBUG"):
        print(message)
