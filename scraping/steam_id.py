import csv
import logging
import os
import sys

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
from data.game_categories import QUERIES

load_dotenv(".env")

FORMAT = '%(asctime)s  %(message)s'
is_logging_mode = os.getenv('LOGGING') == "True"

default_logger_level = logging.FATAL
if is_logging_mode:
    default_logger_level = logging.INFO

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='logs/steam_games.log',
    level=default_logger_level,
    format=FORMAT
)


game_ids = []

BASE_URL = "https://store.steampowered.com/search"

start_idx = int(sys.argv[1])
end_idx = int(sys.argv[2])

def get_url_by_query(driver, q):
    url =  f"{BASE_URL}?term={q}"
    driver.get(url)
    return driver

def get_driver():
    options = webdriver.ChromeOptions()
    options.page_load_strategy = "eager"
    driver = webdriver.Chrome(options=options)
    return driver

logging.info("started parsing steam games ids", )
dr = get_driver()

wait = WebDriverWait(dr, 10)
records = []
output_file = "data/steam_games_id.csv"

file_exists = os.path.isfile(output_file)

with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["id"])
    if not file_exists:
        writer.writeheader()

    for i, q in enumerate(QUERIES[start_idx:end_idx]):
        try:
            page = get_url_by_query(dr, q)
            root = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div#search_resultsRows"))
            )
            game_rows = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.search_result_row"))
            )
            if len(game_rows) <= 1: continue
            for row in game_rows:
                soup = BeautifulSoup(row.get_attribute("outerHTML"), 'html.parser')
                href = soup.find("a")['href']
                game_id = int(href.split("/")[4])
                writer.writerow({"id": game_id})
                
            logging.info("writed %s rows in %s, query_num = %s", len(game_rows), output_file, start_idx + i)
        except TimeoutException:
            # Если элементы не найдены за 2 секунды - пропускаем этот запрос
            logging.warning("нет результатов по запросу %s", q)
            continue
        except Exception as e:
            logging.error("steam games id parser crashed on query %s, error %s", q, e)
            # print(e)
            continue
