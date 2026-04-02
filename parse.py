import json
import sys
import csv
import os

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def get_driver():
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    return driver

page_n = int(sys.argv[1])
category_id = int(sys.argv[2])
output_file = sys.argv[3]


def get_page(driver, n):
    url = f"https://www.kickstarter.com/discover/advanced?category_id={category_id}&sort=magic&page={n}"
    driver.get(url)
    return driver


# page_n = 1
dr = get_driver()
page = get_page(dr, page_n)
wait = WebDriverWait(dr, 10)

root = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "div.grid-container"))
)

cards = wait.until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.js-react-proj-card[data-project]"))
)

records = []
for card in cards:
    desc = card.get_attribute("data-project")
    data_dict = json.loads(desc)
    records.append(data_dict)


file_exists = os.path.isfile(output_file)

fieldnames = [
    'id', 'name', 'blurb', 'goal', 'pledged', \
    'state', 'slug', 'country', 'country_displayable_name', \
    'currency', 'currency_symbol', 'currency_trailing_code', \
    'deadline', 'state_changed_at', 'created_at', 'launched_at', \
    'is_in_post_campaign_pledging_phase', 'staff_pick', 'is_starrable', \
    'disable_communication', 'backers_count', 'static_usd_rate', 'usd_pledged', \
    'converted_pledged_amount', 'fx_rate', 'usd_exchange_rate', 'current_currency', \
    'usd_type', 'creator', 'location', 'category', 'video', 'profile', 'spotlight', \
    'urls', 'percent_funded', 'is_liked', 'is_disliked', 'is_launched', 'prelaunch_activated'
]

with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
    
    # Пишем заголовки только если файл новый
    if not file_exists:
        writer.writeheader()
    
    # Записываем данные
    for record in records:
        writer.writerow(record)
