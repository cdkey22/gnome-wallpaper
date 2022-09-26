import json
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

import requests
from pathlib import Path

WORKING_FOLDER = Path.home() / ".gnome-wallpaper"
GPS_LONGITUDE = "-3.49201"
GPS_LATTITUDE = "48.75201"

NIGHT_WALLPAPER = "/home/cedric/Images/firewatch/night.jpg"
SUNRISE_WALLPAPER = "/home/cedric/Images/firewatch/sunrise.jpg"
MORNING_WALLPAPER = "/home/cedric/Images/firewatch/morning.jpg"
NOON_WALLPAPER = "/home/cedric/Images/firewatch/noon.jpg"
AFTERNOON_WALLPAPER = "/home/cedric/Images/firewatch/afternoon.jpg"
SUNSET_WALLPAPER = "/home/cedric/Images/firewatch/sunset.jpg"

if not WORKING_FOLDER.exists():
    WORKING_FOLDER.mkdir()

DATA_FILE = WORKING_FOLDER / "open-meteo.json"

now = datetime.now()


def fetch_last_version():
    logging.debug("Fetching datas from api ...")
    req = requests.get("https://api.open-meteo.com/v1/forecast",
                       params={
                           "latitude": GPS_LATTITUDE,
                           "longitude": GPS_LONGITUDE,
                           "daily": ["sunrise", "sunset"],
                           "timezone": "auto"
                       }
                       )
    req.raise_for_status()
    data = req.json()["daily"]
    items = {}
    # Copy array to have days
    for sunset in [datetime.strptime(x, "%Y-%m-%dT%H:%M") for x in data["sunset"]]:
        key = sunset.strftime("%Y-%m-%d")
        if key not in items:
            items[key] = {
                "sunrise": 0,
                "sunset": 0
            }
        items[key]["sunset"] = int(sunset.strftime("%s"))

    for sunrise in [datetime.strptime(x, "%Y-%m-%dT%H:%M") for x in data["sunrise"]]:
        key = sunrise.strftime("%Y-%m-%d")
        if key not in items:
            items[key] = {
                "sunrise": None,
                "sunset": None
            }
        items[key]["sunrise"] = int(sunrise.strftime("%s"))

    ret = {}
    for day in items.keys():
        sunrise = items[day]["sunrise"]
        sunset = items[day]["sunset"]
        ret[day] = {
            "sunrise": sunrise,
            "morning": sunrise + 3600,
            "noon": sunrise + ((sunset - sunrise) / 2) - 7200,
            "afternoon": sunrise + ((sunset - sunrise) / 2) + 7200,
            "sunset": sunset,
            "night": sunset + 3600,
        }

    with open(DATA_FILE, 'w', encoding='utf8') as f:
        json.dump(ret, f, ensure_ascii=False)
    logging.debug("Datas fetched from api")


def ensure_good_data():
    if not DATA_FILE.exists():
        fetch_last_version()
    with open(DATA_FILE, 'r', encoding='utf8') as f:
        loaded_data = json.load(f)
    if not now.strftime("%Y-%m-%d") in loaded_data:
        fetch_last_version()


def choose_good_wallpaper():
    with open(DATA_FILE, 'r', encoding='utf8') as f:
        loaded_data = json.load(f)

    logging.debug(f"Now is {now}")

    if not now.strftime("%Y-%m-%d") in loaded_data:
        if now.hour < 8:
            logging.debug(f"Using wallpaper {NIGHT_WALLPAPER}")
            os.system(f"gsettings set org.gnome.desktop.background picture-uri {NIGHT_WALLPAPER}")
        elif now.hour < 9:
            logging.debug(f"Using wallpaper {SUNRISE_WALLPAPER}")
            os.system(f"gsettings set org.gnome.desktop.background picture-uri {SUNRISE_WALLPAPER}")
        elif now.hour < 10:
            logging.debug(f"Using wallpaper {MORNING_WALLPAPER}")
            os.system(f"gsettings set org.gnome.desktop.background picture-uri {MORNING_WALLPAPER}")
        elif now.hour < 11:
            logging.debug(f"Using wallpaper {NOON_WALLPAPER}")
            os.system(f"gsettings set org.gnome.desktop.background picture-uri {NOON_WALLPAPER}")
        elif now.hour < 15:
            logging.debug(f"Using wallpaper {AFTERNOON_WALLPAPER}")
            os.system(f"gsettings set org.gnome.desktop.background picture-uri {AFTERNOON_WALLPAPER}")
        elif now.hour < 18:
            logging.debug(f"Using wallpaper {SUNSET_WALLPAPER}")
            os.system(f"gsettings set org.gnome.desktop.background picture-uri {SUNSET_WALLPAPER}")
        else:
            logging.debug(f"Using wallpaper {NIGHT_WALLPAPER}")
            os.system(f"gsettings set org.gnome.desktop.background picture-uri {NIGHT_WALLPAPER}")

    else:
        data = loaded_data[now.strftime("%Y-%m-%d")]
        logging.debug(f"Sunrise is at {datetime.fromtimestamp(data['sunrise'])}")
        logging.debug(f"Morning is at {datetime.fromtimestamp(data['morning'])}")
        logging.debug(f"Noon is at {datetime.fromtimestamp(data['noon'])}")
        logging.debug(f"Afternoon is at {datetime.fromtimestamp(data['afternoon'])}")
        logging.debug(f"Sunset is at {datetime.fromtimestamp(data['sunset'])}")
        logging.debug(f"Night is at {datetime.fromtimestamp(data['night'])}")

        if now < datetime.fromtimestamp(data["sunrise"]):
            logging.debug(f"Using wallpaper {NIGHT_WALLPAPER}")
            os.system(f"gsettings set org.gnome.desktop.background picture-uri {NIGHT_WALLPAPER}")
        elif now < datetime.fromtimestamp(data["morning"]):
            logging.debug(f"Using wallpaper {SUNRISE_WALLPAPER}")
            os.system(f"gsettings set org.gnome.desktop.background picture-uri {SUNRISE_WALLPAPER}")
        elif now < datetime.fromtimestamp(data["noon"]):
            logging.debug(f"Using wallpaper {MORNING_WALLPAPER}")
            os.system(f"gsettings set org.gnome.desktop.background picture-uri {MORNING_WALLPAPER}")
        elif now < datetime.fromtimestamp(data["afternoon"]):
            logging.debug(f"Using wallpaper {NOON_WALLPAPER}")
            os.system(f"gsettings set org.gnome.desktop.background picture-uri {NOON_WALLPAPER}")
        elif now < datetime.fromtimestamp(data["sunset"]):
            logging.debug(f"Using wallpaper {AFTERNOON_WALLPAPER}")
            os.system(f"gsettings set org.gnome.desktop.background picture-uri {AFTERNOON_WALLPAPER}")
        elif now < datetime.fromtimestamp(data["night"]):
            logging.debug(f"Using wallpaper {SUNSET_WALLPAPER}")
            os.system(f"gsettings set org.gnome.desktop.background picture-uri {SUNSET_WALLPAPER}")
        else:
            logging.debug(f"Using wallpaper {NIGHT_WALLPAPER}")
            os.system(f"gsettings set org.gnome.desktop.background picture-uri {NIGHT_WALLPAPER}")


ensure_good_data()
choose_good_wallpaper()
