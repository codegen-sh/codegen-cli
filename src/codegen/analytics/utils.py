from codegen.env.global_env import global_env


# TODO: move to shared print utils
def print_debug_message(message):
    if global_env.DEBUG:
        print(message)
