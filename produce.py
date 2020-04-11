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

    # Create auphonic object
    auphonic = Auphonic()

    # Collect list of current presets
    current_presets = auphonic.get("presets.json")

    # Search for preset in list of presets
    for preset in current_presets["data"]:
        if preset["preset_name"] == "Pluralsight":
            preset_uuid = preset["uuid"]
            print(f"Preset already exists with UUID {preset_uuid}")
            break

    # For loop exhaused and did not find preset; create new one
    else:

        # Load preset data from JSON file
        print("Preset not found; creating now")
        with open("pluralsight_preset.json", "r") as handle:
            preset_data = json.load(handle)

        # Create new preset and print UUID for confirmation
        add_preset = auphonic.post("presets.json", jsonbody=preset_data)
        preset_uuid = add_preset["data"]["uuid"]
        print(f"Preset added with UUID {preset_uuid}")

    # Find all .wav files and iterate over the list
    for input_file in auphonic.find_files("wav"):
        print(f"\nStarting {input_file}")

        # Create the production body referencing the preset and extra metadata
        prod_data = {"preset": preset_uuid, "metadata": {"title": input_file}}

        # Create a new production and extract the production UUID
        add_prod = auphonic.post("productions.json", jsonbody=prod_data)
        prod_uuid = add_prod["data"]["uuid"]
        print(f"Production added with UUID {prod_uuid}")

        # Upload a file data, NOT a JSON payload nor a filename string
        print(f"Uploading {input_file} ...", end="")
        with open(input_file, "rb") as handle:
            auphonic.post(
                f"production/{prod_uuid}/upload.json",
                files={"input_file": handle},
            )
        print(" OK!")

        # Start the production
        auphonic.post(f"production/{prod_uuid}/start.json")

        # Wait for production to complete and download file
        print(f"Producting and downloading file ...", end="")
        auphonic.download_file(prod_uuid)
        print(" OK!")


if __name__ == "__main__":
    main()
