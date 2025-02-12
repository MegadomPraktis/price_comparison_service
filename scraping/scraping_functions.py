# scraping/scraping_functions.py

import time
import random
import requests
from bs4 import BeautifulSoup
from config import PRAKTIS_SEARCH_URL, PRAKTIKER_SEARCH_URL, USER_AGENTS

# Create a session instance locally
session = requests.Session()
session.headers.update({"Accept-Language": "en-US,en;q=0.9"})

def get_soup(url):
    for attempt in range(3):
        try:
            session.headers.update({"User-Agent": random.choice(USER_AGENTS)})
            response = session.get(url, timeout=17)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException:
            time.sleep(2 ** attempt + random.uniform(1, 2.5))
    return None

def fetch_product_data_praktis(code):
    code = str(code).strip()
    url = PRAKTIS_SEARCH_URL.format(code)
    soup = get_soup(url)
    if not soup:
        return {"code": code, "name": "N/A", "url": url, "regular_price": "N/A", "promo_price": "N/A"}
    name = soup.select_one("p.product-name.h4")
    regular_price = (soup.select_one("span.price.striked, div.old-price span.price")
                     or soup.select_one("span.price"))
    promo_price = soup.select_one("div.special-price span.price")
    return {
        "code": code,
        "name": name.text.strip() if name else "N/A",
        "url": url,
        "regular_price": regular_price.text.strip().replace("\u043b\u0432.", "").strip() if regular_price else "N/A",
        "promo_price": promo_price.text.strip().replace("\u043b\u0432.", "").strip() if promo_price else None,
    }

def fetch_product_data_praktiker(code):
    code = str(code).strip()
    url = PRAKTIKER_SEARCH_URL.format(code)
    soup = get_soup(url)
    if not soup:
        return {"code": code, "name": "N/A", "url": url, "regular_price": None, "promo_price": None}
    name_element = soup.select_one("h2.product-item__title a")
    name = name_element.text.strip() if name_element else "N/A"
    regular_price = None
    promo_price = None
    old_price_element = soup.select_one("span.product-price--old .product-price__value")
    old_price_sup = old_price_element.find_next("sup") if old_price_element else None
    if old_price_element:
        regular_price = old_price_element.text.strip()
        if old_price_sup:
            regular_price += "." + old_price_sup.text.strip()
    else:
        regular_price_element = soup.select_one("span.product-price__value, span.price__value")
        regular_price_sup = regular_price_element.find_next("sup") if regular_price_element else None
        if regular_price_element:
            regular_price = regular_price_element.text.strip()
            if regular_price_sup:
                regular_price += "." + regular_price_sup.text.strip()
    promo_price_element = soup.select_one("div.product-store-prices__item > span.product-price:not(.product-price--old) span.product-price__value")
    promo_price_sup = promo_price_element.find_next("sup") if promo_price_element else None
    if promo_price_element:
        promo_price = promo_price_element.text.strip()
        if promo_price_sup:
            promo_price += "." + promo_price_sup.text.strip()
    return {
        "code": code,
        "name": name,
        "url": url,
        "regular_price": regular_price,
        "promo_price": promo_price,
    }
