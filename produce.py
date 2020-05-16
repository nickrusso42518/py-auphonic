#!/usr/bin/env python

"""
Author: Nick Russo (njrusmc@gmail.com)
Purpose: Example script for use with Pluralsight video training.
"""

import json
from auphonic import Auphonic


def main():
    """
    Execution starts here.
    """

    # Use class-level helper method to build new object (handy for shell runs)
    auphonic = Auphonic.build_from_env_vars()

    # Load in the preset dictionary from a file
    with open("pluralsight_preset.json", "r") as handle:
        new_preset = json.load(handle)

    # Create the preset if necessary, or do nothing if it already exists.
    # Retain the UUID for reference later when processing files
    preset_uuid = auphonic.create_preset(new_preset)

    # Find all .wav files and iterate over the list. Ensure the downloaded
    # file size is greater than 50,000 bytes to avoid false positives
    for input_file in auphonic.find_files("wav"):
        assert auphonic.process_file(input_file, preset_uuid) > 50000


if __name__ == "__main__":
    main()
