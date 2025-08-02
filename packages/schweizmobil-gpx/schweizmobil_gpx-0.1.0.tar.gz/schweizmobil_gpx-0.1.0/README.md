# schweizmobil_gpx

Download all your saved GPX tours from [schweizmobil.ch](https://www.schweizmobil.ch/) in one go.

## 📍 Background

Schweizmobil is a popular platform for planning hiking, biking, and other outdoor tours in Switzerland. 
I had over 100 personal tours saved and wanted to download them automatically instead of one by one manually. 


## 🧠 What This Package Does

- Uses your personal `auth` cookie to access your account
- Fetches all saved tours
- Downloads each one as a `.gpx` file into a folder of your choice


## 🛠 Installation

You can install this using pip.

pip install schweizmobil_gpx

## 🧾 Usage

### 1. Get your authentication cookie

Using Chrome:

- Log into [schweizmobil.ch](https://www.schweizmobil.ch/)
- Right-click → **Inspect** (or press `Cmd + Option + I`)
- Go to the **Application** tab
- Under **Cookies**, click the `https://www.schweizmobil.ch` domain
- Look for a cookie named `auth`
- Copy its **value** — a long string of letters and symbols

### 2. Run the downloader


from schweizmobil_gpx import download_gpx_tours
download_gpx_tours("your_auth_cookie_here")

*All .gpx files will be saved in the current directory.


## 📂 Output

Each file is saved as a `.gpx` and named after your tour:

Example:
Pilatus_Hike.gpx
Bike_Ride_Zurich.gpx


## 📦 Requirements

This package depends on:

- `requests`

## 🔐 License

Licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).

## 🚧 Notes

- This is an **unofficial** tool, not affiliated with SchweizMobil
- Requires a valid cookie from a logged-in session
- Works best with saved tours in your personal account
