# https://auphonic.com/api/{presets|productions}.json

import json
import os
import time
import requests

BASE_URL = "https://auphonic.com/api"


def main():

    # Collect username, password, and input directory from environment variables
    username = os.environ.get("AUPHONIC_USERNAME")
    if not username:
        raise ValueError("Must define AUPHONIC_USERNAME environment variable")

    password = os.environ.get("AUPHONIC_PASSWORD")
    if not password:
        raise ValueError("Must define AUPHONIC_PASSWORD environment variable")

    # If not supplied, use the "auphonic" directory on the desktop
    input_dir = os.environ.get("AUPHONIC_INPUT_DIR")
    if not input_dir:
        input_dir = f"{os.path.expanduser('~/Desktop')}/auphonic"
        print(f"AUPHONIC_INPUT_DIR not supplied; using {input_dir}")

    # Ensure the directory exists; creating it would be useless
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"input directory {input_dir} does not exist")

    # Assemble HTTP basic auth 2-tuple for authentication
    http_auth = (username, password)
    session = requests.session()

    # Get current presets
    current_presets = to_dict(
        session.get(f"{BASE_URL}/presets.json", auth=http_auth)
    )

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
        add_preset = to_dict(
            session.post(
                f"{BASE_URL}/presets.json", auth=http_auth, json=preset_data
            )
        )
        preset_uuid = add_preset["data"]["uuid"]
        print(f"Preset added with UUID {preset_uuid}")

    f = "test.wav"

    # Create the production body referencing the preset and extra metadata
    prod_data = {"preset": preset_uuid, "metadata": {"title": f}}

    # everything below needs to go in a loop for each file

    # Create a new production
    add_prod = to_dict(
        session.post(
            f"{BASE_URL}/productions.json", auth=http_auth, json=prod_data
        )
    )

    # Extract the production UUID so we can upload files and print confirmation
    prod_uuid = add_prod["data"]["uuid"]
    print(f"Production added with UUID {prod_uuid}")

    # Upload a file, NOT a JSON payload
    file_str = f"{input_dir}/{f}"
    print(f"Uploading {file_str} ...", end="")

    with open(file_str, "rb") as payload:
        upload_file = to_dict(
            session.post(
                f"{BASE_URL}/production/{prod_uuid}/upload.json",
                auth=http_auth,
                files={"input_file": payload},
            )
        )
    print(" OK!")

    # Start the production and store reuslts
    start_prod = to_dict(
        session.post(
            f"{BASE_URL}/production/{prod_uuid}/start.json", auth=http_auth
        )
    )

    print(f"Producing audio ...", end="")

    # Keep looping until the download URL is populated
    dl_url = None
    while not dl_url:
        print(".", end="", flush=True)
        time.sleep(2)
        start_prod = to_dict(
            session.get(
                f"{BASE_URL}/production/{prod_uuid}.json", auth=http_auth
            )
        )
        dl_url = start_prod["data"]["output_files"][0]["download_url"]

    print(" OK!")

    # Download the file using the download URL
    print(f"Downloading file from {dl_url}")
    dl_file = session.get(dl_url, auth=http_auth)

    # Create auphonic-results directory within the input directory if
    # it does not already exist
    output_dir = f"{input_dir}/auphonic-results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Store the new file prefixed with "auphonic-"
    with open(f"{output_dir}/auphonic-{f}", "wb") as handle:
        handle.write(dl_file.content)


def to_dict(response):
    """
    Helper function to ensure HTTP requests succeed and to return the
    JSON body as Python bojects.
    """
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    main()
