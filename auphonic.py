#!/usr/bin/env python

"""
Author: Nick Russo (njrusmc@gmail.com)
Purpose: A simple Python client library for interacting with Auphonic
via the REST API. See documentation here: https://auphonic.com/help/api/
"""

import os
import glob
import time
import requests


class Auphonic:
    """
    Stateful handler for the Auphonic REST API.
    """

    def __init__(self):
        """
        Constructor loads in environment variables, checks input directory,
        creates output directory, and stores attributes for use later.
        """
        # Collect username, password, and input directory from env vars
        username = os.environ.get("AUPHONIC_USERNAME")
        if not username:
            raise ValueError("Must define AUPHONIC_USERNAME environment var")

        password = os.environ.get("AUPHONIC_PASSWORD")
        if not password:
            raise ValueError("Must define AUPHONIC_PASSWORD environment var")

        # If not supplied, use the "auphonic" directory on the desktop
        input_dir = os.environ.get("AUPHONIC_INPUT_DIR")
        if not input_dir:
            input_dir = f"{os.path.expanduser('~/Desktop')}/auphonic"
            print(f"AUPHONIC_INPUT_DIR not supplied; using {input_dir}")

        # Ensure the directory exists; creating it would be useless
        if not os.path.exists(input_dir):
            raise FileNotFoundError(f"input dir {input_dir} does not exist")

        # Store object attributes
        self.http_auth = (username, password)
        self.input_dir = input_dir
        self.session = requests.session()

        # Build output directory
        self.output_dir = f"{self.input_dir}/auphonic-results"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _req(self, resource, method, jsonbody=None, files=None):
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
        return self._req(method="get", resource=resource)

    def post(self, resource, jsonbody=None, files=None):
        """
        Issue a POST request to Auphonic for a given resource. This can include
        a JSON body or files for uploading.
        """
        return self._req(
            method="post", resource=resource, jsonbody=jsonbody, files=files
        )

    def find_files(self, file_extension):
        """
        Search for files in the input directory for a given file extension.
        Examples include "wav" or "mp3".
        """
        return glob.glob(f"{self.input_dir}/*.{file_extension}")

    def download_file(self, prod_uuid):
        """
        Performs the complex actions needed to download a file from
        a given production. This assumes that there is only one file
        for simplicity. The file is written to the output directory
        prefixed with "auphonic-" to differentiate it from the source.
        """

        # Keep looping until the download URL is populated
        dl_url = None
        while not dl_url:
            time.sleep(2)
            start_prod = self.get(f"production/{prod_uuid}.json")
            dl_url = start_prod["data"]["output_files"][0]["download_url"]

        # Download the file using the download URL. Cannot use get()
        # helper as it will include the base_url twice
        dl_file = self.session.get(dl_url, auth=self.http_auth)

        # Determine the original filename by extracting it from the URL, then
        # write the auphonic-(orig_file) file to disk
        orig_file = dl_file.url.split("/")[-1]
        with open(f"{self.output_dir}/auphonic-{orig_file}", "wb") as handle:
            handle.write(dl_file.content)
