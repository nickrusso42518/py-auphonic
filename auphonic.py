#!/usr/bin/env python

"""
Author: Nick Russo (njrusmc@gmail.com)
Purpose: A simple Python client library for interacting with Auphonic
via the REST API. See documentation here: https://auphonic.com/help/api/
"""

from glob import glob
from enum import Enum
import logging
import os
import time
import requests


class Status(Enum):
    """
    Enumerated status codes collected from this resource:
    https://auphonic.com/api/info/production_status.json
    """

    FILE_UPLOAD = 0
    WAITING = 1
    ERROR = 2
    DONE = 3
    AUDIO_PROC = 4
    AUDIO_ENC = 5
    OUT_FILE_XFER = 6
    MONO_MIX = 7
    SPLIT_AUDIO = 8
    INCOMPLETE = 9
    NOT_STARTED = 10
    OUTDATED = 11
    IN_FILE_XFER = 12
    STOP_PROD = 13
    SPEECH_REC = 14


class Auphonic:
    """
    Stateful handler for the Auphonic REST API.
    """

    def __init__(self, username, password, input_dir=None, log_level=logging.INFO):
        """
        Constructor loads in environment variables, checks input directory,
        creates output directory, and stores attributes for use later.
        The "log_level" option identifies the level of logging required,
        which is INFO by default.
        """

        # Craete a simple logger set to specific log level
        logging.basicConfig(
            format="%(asctime)s %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            level=log_level,
        )
        self.logger = logging.getLogger()

        # Store the object's ID to improve logging cardinality
        _id = id(self)
        self.logger.info("Creating auphonic for user %s, id %s", username, _id)

        # If not supplied, use the "auphonic" directory on the desktop
        if not input_dir:
            input_dir = "test_files"

        # Ensure the directory exists; creating it would be useless
        if not os.path.exists(input_dir):
            raise FileNotFoundError(f"input dir {input_dir} does not exist")

        # Store object attributes
        self.http_auth = (username, password)
        self.input_dir = input_dir
        self.session = requests.session()
        self.logger.info("Assigned input_dir %s, id %s", input_dir, _id)

        # Build output directory if it doesn't already exist
        self.output_dir = f"{self.input_dir}/auphonic-results"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.logger.info("Completed auphonic for user %s, id %s", username, _id)

    @staticmethod
    def build_from_env_vars(log_level=logging.INFO):
        """
        Static class-level helper method to quickly create a new Auhponic
        object using environment variables:
          1. AUPHONIC_USERNAME: Your personal username for Auphonic
          2. AUPHONIC_PASSWORD: Your personal password for Auphonic
          3. AUPHONIC_INPUT_DIR: Local path to audio input files (optional)
        """

        # Collect username, password, and input directory from env vars
        username = os.environ.get("AUPHONIC_USERNAME")
        if not username:
            raise ValueError("Must define AUPHONIC_USERNAME environment var")

        password = os.environ.get("AUPHONIC_PASSWORD")
        if not password:
            raise ValueError("Must define AUPHONIC_PASSWORD environment var")

        input_dir = input_dir = os.environ.get("AUPHONIC_INPUT_DIR")

        # Create and return new Auphonic object
        return Auphonic(
            username=username,
            password=password,
            input_dir=input_dir,
            log_level=log_level,
        )

    def request(self, resource, method, jsonbody=None, files=None):
        """
        Basic wrapper for requests using existing authentication, base URL,
        and other attributes for simplicity.
        """

        # Define base URL and issue request
        base_url = "https://auphonic.com/api"
        resp = self.session.request(
            method=method,
            url=f"{base_url}/{resource}",
            json=jsonbody,
            files=files,
            auth=self.http_auth,
        )

        # Check for errors and return body as Python objects
        resp.raise_for_status()
        return resp.json()

    def get(self, resource):
        """
        Issue a GET request to Auphonic for a given resource.
        """
        return self.request(method="get", resource=resource)

    def post(self, resource, jsonbody=None, files=None):
        """
        Issue a POST request to Auphonic for a given resource. This can include
        a JSON body or files for uploading.
        """
        return self.request(
            method="post", resource=resource, jsonbody=jsonbody, files=files
        )

    def create_preset(self, new_preset):
        """
        Creates a new preset using the supplied dictionary. If the preset
        already exists, nothing happens. Otherwise, a new preset is created.
        """

        # Perform a quick check to ensure the preset has a required key
        if "preset_name" not in new_preset.keys():
            raise ValueError("Preset is missing required 'preset_name' key")

        # Store preset name and collect list of current presets
        new_name = new_preset["preset_name"].lower()
        self.logger.info("Starting create preset for %s", new_name)
        current_presets = self.get("presets.json")

        # Search for preset in list of presets
        for preset in current_presets["data"]:
            if preset["preset_name"].lower() == new_name:
                uuid = preset["uuid"]
                self.logger.info(
                    "Preset %s already exists with UUID %s", new_name, uuid
                )
                break

        # For loop exhaused and did not find preset; create new one
        else:

            # Create new preset and print UUID for confirmation
            self.logger.info("Preset %s not found; creating now", new_name)
            add_preset = self.post("presets.json", jsonbody=new_preset)
            uuid = add_preset["data"]["uuid"]
            self.logger.info("Preset %s added with UUID %s", new_name, uuid)

        # Return the preset UUID for reference later
        return uuid

    def find_files(self, file_extension):
        """
        Search for files in the input directory for a given file extension.
        Examples include "wav" or "mp3".
        """
        return glob(f"{self.input_dir}/*.{file_extension}")

    def create_production(self, input_file, preset_uuid):
        """
        Creates a new, empty production to encapsulate a given input_file
        using an existing preset. Returns the production UUID which is
        used for follow-on activities such as uploading files and
        producing audio.
        """

        self.logger.info("Starting prod record for %s", input_file)

        # Create the production body referencing the preset and extra metadata
        prod_data = {"preset": preset_uuid, "metadata": {"title": input_file}}

        # Create a new production and extract the production UUID
        add_prod = self.post("productions.json", jsonbody=prod_data)

        prod_uuid = add_prod["data"]["uuid"]
        self.logger.info(
            "Completed prod record for %s, uuid %s", input_file, prod_uuid
        )

        # Return the production UUID for reference later
        return prod_uuid

    def upload_file(self, input_file, prod_uuid):
        """
        Populate an existing production, referenced by UUID, with the
        specified input file. This method blocks until the upload
        is complete (synchronous).
        """

        # Upload a file data, NOT a JSON payload nor a filename string
        self.logger.info("Starting file upload for %s", input_file)
        with open(input_file, "rb") as handle:
            files = {"input_file": handle}
            self.post(f"production/{prod_uuid}/upload.json", files=files)
        self.logger.info("Completed file upload for %s", input_file)

    def produce_audio(self, prod_uuid):
        """
        Given a production and input file, begins the audio production process.
        It waits until the download URL is available, then returns that URL.
        If an error occurs (or some other unsuccessful status code that
        represents processing is complete), displays the error message
        and returns None to signal failure.
        """

        # Start producing the audio. This API call is non-blocking
        # (asynchronous) and we must wait until the "download_url" is present
        self.logger.info("Starting  audio prod for %s", prod_uuid)
        self.post(f"production/{prod_uuid}/start.json")

        # Keep looping until the complete; either DONE or ERROR
        # Intermediate steps may be WAITING, AUDIO_PROC, or AUDIO_ENC
        cur_status = Status.WAITING
        while cur_status not in [Status.DONE, Status.ERROR]:
            time.sleep(3)
            self.logger.info("%s file DL URL for prod %s", cur_status, prod_uuid)
            start_prod = self.get(f"production/{prod_uuid}.json")
            cur_status = Status(start_prod["data"]["status"])

        # Success; return the download URL for use later
        if cur_status == Status.DONE:
            download_url = start_prod["data"]["output_files"][0]["download_url"]
            self.logger.info("%s for %s - %s", cur_status, prod_uuid, download_url)
            return download_url

        # Error occurred; log error message and return None
        error_msg = start_prod["data"]["error_message"]
        self.logger.info("%s for %s - %s", cur_status, prod_uuid, error_msg)
        return None

    def download_file(self, download_url):
        """
        Performs the complex actions needed to download a file from
        a given production. This assumes that there is only one file
        for simplicity. The file is written to the output directory
        prefixed with "auphonic-" to differentiate it from the source.
        """

        self.logger.info("Starting file download from URL %s", download_url)

        # Download the file using the download URL. Cannot use get()
        # helper as it will include the base_url twice
        dl_file = self.session.get(download_url, auth=self.http_auth)

        # Determine the original filename by extracting it from the URL, then
        # write the auphonic-(orig_file) file to disk
        orig_file = dl_file.url.split("/")[-1]
        outfile = f"{self.output_dir}/auphonic-{orig_file}"
        with open(outfile, "wb") as handle:
            handle.write(dl_file.content)

        # Extract the filesize in bytes (parse int from str) for confirmation
        size_bytes = int(dl_file.headers["Content-Length"])
        self.logger.info("Completed file download from URL %s", download_url)
        self.logger.info("Outfile %s size: %s bytes", outfile, size_bytes)

        # Return the filesize; caller may want to process it
        return size_bytes

    def process_file(self, input_file, preset_uuid):
        """
        Executes a common workflow to process a single audio file using
        the parameters in a given preset. Returns the file size in bytes.
          1. Creates a new production for the file
          2. Uploads the file
          3. Produces audio for the file
          4. Downfiles the Auphonic output file if the previous step succeeded
        """

        # Perform the aforementioned steps in sequence
        prod_uuid = self.create_production(input_file, preset_uuid)
        self.upload_file(input_file, prod_uuid)
        download_url = self.produce_audio(prod_uuid)

        # Only try to download the file if the processing succeeded
        if download_url:
            return self.download_file(download_url)

        # 0 bytes produced; signals failure
        return 0
