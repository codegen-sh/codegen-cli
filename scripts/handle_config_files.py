#!/usr/bin/env python3
import glob
import os
import subprocess


def get_current_tag():
    try:
        # Get tag from git? TODO: there may be a better way to do this
        result = subprocess.run(['git', 'describe', '--tags', '--exact-match'],
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def handle_config_files():
    current_tag = get_current_tag()
    if not current_tag:
        print("No tag found")
        return

    # If tag contains 'dev', remove all .config.* files except .config.production
    # The idea here is to eliminate non prod configuration from being published
        config_files = glob.glob('.config.*')
        for config_file in config_files:
            if config_file != '.config.production':
                try:
                    os.remove(config_file)
                    print(f"Removed {config_file}")
                except OSError as e:
                    print(f"Error removing {config_file}: {e}")
    else:
        print("Not a dev tag, keeping all config files")

if __name__ == "__main__":
    handle_config_files()
