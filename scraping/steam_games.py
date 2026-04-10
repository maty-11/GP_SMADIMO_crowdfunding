import os
import sys
import csv
import logging
import requests

from dotenv import load_dotenv


load_dotenv(".env")

FORMAT = '%(asctime)s  %(message)s'
BASE_URl = "https://store.steampowered.com/api/appdetails"
REVIEW_URL = "https://store.steampowered.com/appreviews"


is_logging_mode = os.getenv('LOGGING') == "True"

cols_to_save = [
    'type', 'name', 'is_free', \
    'short_description', 'supported_languages', 'header_image', \
    'price_overview', 'recommendations', \
    'categories', 'genres', 'release_date', \
    'ratings',
]

default_logger_level = logging.FATAL
if is_logging_mode:
    default_logger_level = logging.INFO

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='logs/steam_games.log',
    level=default_logger_level,
    format=FORMAT
)

start_idx, end_idx = int(sys.argv[1]), int(sys.argv[2])

game_ids = []

with open('data/steam_games_id.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for game_id in reader:
        if game_id not in game_ids:
            game_ids.append(game_id)


def get_game_details(app_id):
    print(app_id)
    url = f"{BASE_URl}?appids={app_id}"
    response = requests.get(url)
    data = response.json()

    if data[str(app_id)]['success']:
        game_data = data[app_id]['data']
        return {x: game_data[x] for x in cols_to_save if x in game_data.keys()}
    else:
        logger.warning("not found id %s", app_id)
        return None
    

output_file = "data/steam_games.csv"

file_exists = os.path.isfile(output_file)

with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=cols_to_save)
    if not file_exists:
        writer.writeheader()


    for i, steam_game_id in enumerate(game_ids[start_idx:end_idx]):
        try:
            game_details = get_game_details(steam_game_id["id"])
            if game_details:
                writer.writerow(game_details)
                logger.info("game %s saved, n=%s", game_details["name"], i+start_idx)
        except Exception as e:
                logger.error("game with id %s failed to load", steam_game_id)
