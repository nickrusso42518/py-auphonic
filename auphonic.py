#!/usr/bin/env python

import requests


class Auphonic:
    def __init__(self):
        # Collect username, password, and input directory from environment variables
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
        self.output_dir = output_dir = f"{self.input_dir}/auphonic-results"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.session = requests.session()

    def _req(self, resource, method, jsonbody=None, files=None):
        base_url = "https://auphonic.com/api"
        resp = self.session.request(
            method=method,
            url=f"{base_url}/{resource}",
            json=jsonbody,
            files=files,
            auth=self.http_auth,
        )
        resp.raise_for_status()
        return resp.json()

    def get(self, resource):
        return _req(method="get", resource=resource)

    def post(self, resource, jsonbody=None, files=None):
        return _req(method="post", resource=resource, jsonbody=None, files=None)
