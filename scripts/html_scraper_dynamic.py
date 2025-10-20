from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import csv
import os
import datetime
import time

# Target URLs
URLS = [
    "https://www.msn.com/en-us/news",
    "https://www.yahoo.com/news",
    "https://www.cnn.com",
    "https://www.foxnews.com",
]

# Setup headless browser
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)

# Output path
today = datetime.date.today().isoformat()
output_dir = "data/raw"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, f"headlines_dynamic_{today}.csv")

# Collect headlines
headlines = set()

for url in URLS:
    try:
        driver.get(url)
        time.sleep(5)  # Let JS render

        # Extract visible text from headline-like tags
        elements = driver.find_elements(By.XPATH, "//h1|//h2|//h3|//a")
        for el in elements:
            text = el.text.strip()
            if text and len(text.split()) > 4:
                headlines.add(text)

    except Exception as e:
        print(f"Error scraping {url}: {e}")

driver.quit()

# Write to pipe-delimited CSV
with open(output_path, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file, delimiter="|")
    writer.writerow(["headline"])
    for headline in sorted(headlines):
        writer.writerow([headline])

print(f"Scraped {len(headlines)} headlines from dynamic sites to: {output_path}")
