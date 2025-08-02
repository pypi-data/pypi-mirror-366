#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 27 18:13:02 2025
"""


import requests


def download_gpx_tours(auth_cookie):
    cookies = {"auth": auth_cookie}  # Use your real auth cookie value here

    # Step 1: Get your list of tours
    response = requests.get(
        "https://schweizmobil.ch/api/6/tracks", cookies=cookies
    )
    data = response.json()

    # Step 2: Loop through tours and download each GPX
    for track in data["items"]:
        track_id = track["id"]
        name = track["name"].replace(" ", "_") + ".gpx"
        gpx_url = f"https://schweizmobil.ch/api/6/tracks/{track_id}/export_gps"

        print(f"Downloading: {name}")
        gpx_response = requests.get(gpx_url, cookies=cookies)
        gpx_response.raise_for_status()  # Error Handling if requests fails

        with open(name, "wb") as f:
            f.write(gpx_response.content)
