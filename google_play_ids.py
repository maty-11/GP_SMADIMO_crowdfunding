from game_categories import QUERIES

import json
import sys
import csv
import os

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from google_play_ids import QUERIES

BASE_URL = "https://play.google.com/store/search?hl=en&c=apps"

def get_url_by_query(driver, q):
    url =  f"{BASE_URL}&q={q}"
    driver.get(url)
    return driver

def get_driver():
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    return driver


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
        except TimeoutException:
            # Если элементы не найдены за 2 секунды - пропускаем этот запрос
            print(f"нет результатов по запросу {q}")
            continue
        except Exception as e:
            continue
