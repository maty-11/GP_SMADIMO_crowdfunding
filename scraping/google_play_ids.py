import csv
import os
import logging

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv

from data.game_categories import QUERIES

load_dotenv('.env')
            
FORMAT = '%(asctime)s  %(message)s'
is_logging_mode = os.getenv('LOGGING') == "True"

default_logger_level = logging.FATAL
if is_logging_mode:
    default_logger_level = logging.INFO

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='logs/google_play.log',
    level=default_logger_level,
    format=FORMAT
)

BASE_URL = "https://play.google.com/store/search?hl=en&c=apps"

def get_url_by_query(driver, q):
    url =  f"{BASE_URL}&q={q}"
    driver.get(url)
    return driver

def get_driver():
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    return driver

logging.info("started parsing google_play_ids", )
dr = get_driver()

wait = WebDriverWait(dr, 10)
records = []
output_file = "games_id.csv"

file_exists = os.path.isfile(output_file)

with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["id"])
    if not file_exists:
        writer.writeheader()

    for q in QUERIES:
        try:
            page = get_url_by_query(dr, q)
            root = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.ftgkle"))
            )
            game_cards = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.ULeU3b"))
            )
            if len(game_cards) <= 1: continue
            for card in game_cards:
                soup = BeautifulSoup(card.get_attribute("innerHTML"), 'html.parser')
                href = soup.find("a")['href']
                game_id = href.split("?id=")
                if game_id and len(game_id) > 1:
                    game_id = game_id[1]
                if game_id and '[' not in game_id:
                    print(game_id, href)
                    writer.writerow({"id": game_id})
            logging.info("writed %s rows in %s", len(game_cards), output_file)
        except TimeoutException:
            # Если элементы не найдены за 2 секунды - пропускаем этот запрос
            logging.warning("нет результатов по запросу %s", q)
            continue
        except Exception as e:
            logging.error("google_play_ids parser crashed on query %s, error %s", q, e)
            continue
