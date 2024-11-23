import requests
from bs4 import BeautifulSoup
import json
import re
import logging
from typing import List, Dict

# Set up logging
logging.basicConfig(level=logging.INFO)

# Constants
URL = "https://www.motoreststaraposta.cz/poledni-nabidka/"
OUTPUT_PATH = "menu.json"

# Function to remove extra spaces
def remove_extra_spaces(text: str) -> str:
    return " ".join(text.split())

# Function to extract menu data from soup
def extract_menu_data(soup: BeautifulSoup) -> List[Dict[str, str]]:
    menu_items = soup.find_all("font", class_="wsw-02")
    menu_data = []
    current_dish = ""
    current_price = ""

    for item in menu_items:
        menu_text = item.get_text(strip=True)

        # Check if the text starts with a number (indicates menu item)
        if not re.match(r"^\d+\.", menu_text):
            continue

        # Find price at the end of the line
        match = re.search(r"(\d+,\-)$", menu_text)
        if match:
            current_price = match.group(0) + " Kč"
            name = menu_text.replace(match.group(0), "").strip()
            full_dish = remove_extra_spaces(current_dish + " " + name)
            menu_data.append({"Dish": full_dish, "Price": current_price})
            current_dish = ""  # Reset after adding the item
        else:
            # Combine name and description if price is not found
            current_dish = current_dish + " " + menu_text if current_dish else menu_text

    return menu_data

# Function to fetch page content
def fetch_page_content(url: str) -> BeautifulSoup:
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status
        return BeautifulSoup(response.content, "html.parser")
    except requests.RequestException as e:
        logging.error("Failed to fetch page content: %s", e)
        raise

# Function to save menu data to JSON file
def save_to_json(data: List[Dict[str, str]], filepath: str) -> None:
    try:
        with open(filepath, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        logging.info("Menu data saved to %s", filepath)
    except IOError as e:
        logging.error("Failed to save data to JSON: %s", e)

def main():
    soup = fetch_page_content(URL)
    menu_data = extract_menu_data(soup)
    save_to_json(menu_data, OUTPUT_PATH)
    logging.info("Extracted menu data: %s", json.dumps(menu_data, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
