import csv
import requests
from dotenv import load_dotenv
import os
import sys

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

load_dotenv()

game_ids = []


with open('games_id.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for game_id in reader:
        game_ids.append(game_id)

BASE_URL = "https://play.google.com/store/apps/details"
# https://play.google.com/store/apps/details?id=com.tutotoons.app.mybabyunicorn.free

def get_game_by_id(driver, id):
    url =  f"{BASE_URL}?id={id}"
    driver.get(url)
    return driver

def get_driver():
    options = webdriver.ChromeOptions()
    options.page_load_strategy = "eager"
    driver = webdriver.Chrome(options=options)
    return driver


dr = get_driver()

wait = WebDriverWait(dr, 10)
records = []

start_c = int(sys.argv[1])
end_c = int(sys.argv[2])

c = start_c

for game_row in game_ids[c:]:
    game_id = game_row["id"]
    try:
        if "[" in game_id: continue
        if c % 10 == 0: print(c)


        page = get_game_by_id(dr, game_id)
        root = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.T4LgNb"))
        )

        game_html = root.get_attribute("innerHTML")
        game_soup = BeautifulSoup(game_html, "html.parser")
        readable_name = game_soup.find("span", class_="AfwdI").get_text()

        root_info = game_soup.find("div", class_="w7Iutd")
        ratings_node = list(root_info.children)[0]
        raiting = ratings_node.find("div", class_="TT9eCd").get_text()

        download_amount = list(root_info.children)[1]
        dwnl = download_amount.find("div", class_="ClM7O").get_text()

        tags_holder = game_soup.find("div", class_="Uc6QCc")
        tags = []
        for tag_element in tags_holder.children:
            
            tag_name = tag_element.find("span").get_text()
            tags.append(tag_name)
        records.append({
            "id": game_id,
            "name": readable_name,
            "rating": raiting,
            "download": dwnl,
            "tags": ",".join(tags)
        })
        # print(records[-1])
        c += 1
        if c == end_c: break
    except Exception as e:
        print(f"no data to url {game_id}")
        continue


output_filename = 'google_play_games_data.csv'

file_exists = os.path.isfile(output_filename) and os.path.getsize(output_filename) > 0

with open(output_filename, 'a', encoding='utf-8', newline='') as csvfile:
    fieldnames = records[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    if not file_exists:
        writer.writeheader()

    writer.writerows(records)
