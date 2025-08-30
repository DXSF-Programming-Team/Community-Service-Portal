import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from PIL import Image
import requests
from io import BytesIO


FACULTY_LIST = "faculty_list.json"
FACULTY_URL = "https://www.dextersouthfield.org/about-us/directory"

def save_faculty_images(faculty_data):
    for faculty in faculty_data:
        if faculty["photo"]:
            photo_url = faculty["photo"]
            response = requests.get(photo_url)
            image = Image.open(BytesIO(response.content))
            image.save(f"static/faculty_images/{faculty['serial_id']}.jpg")

def scrape_faculty():
    options = Options()
    #options.add_argument("--headless=new")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    if not os.path.exists(FACULTY_LIST):
        driver.get(FACULTY_URL)

        wait = WebDriverWait(driver, 10)
        sleep(4)
        
        faculty_data = []
        scraping = True
        serial_id = 0
        
        while scraping:
            faculty_wrapper = driver.find_element(By.ID, "fsEl_14193")
            if (faculty_wrapper.get_attribute("aria-busy") == "true"):
                sleep(1)

            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "fsConstituentItem")))
            faculty_constituents = driver.find_elements(By.CLASS_NAME, "fsConstituentItem")

            for faculty_constituent in faculty_constituents:
                serial_id += 1

                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "fsPhoto")))
                photo_wrapper = faculty_constituent.find_element(By.CLASS_NAME, "fsPhoto")
                photo_url = photo_wrapper.find_element(By.TAG_NAME, "img").get_attribute("src")

                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "fsFullName")))
                name_wrapper = faculty_constituent.find_element(By.CLASS_NAME, "fsFullName")
                name = name_wrapper.find_element(By.TAG_NAME, "a").text
                print(f"Found name: {name}")

                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "fsTitles")))
                title = faculty_constituent.find_element(By.CLASS_NAME, "fsTitles").text

                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "fsEmail")))
                try:
                    email_wrapper = faculty_constituent.find_element(By.CLASS_NAME, "fsEmail")
                    email_div = email_wrapper.find_element(By.TAG_NAME, "div")
                    email = email_div.find_element(By.TAG_NAME, "a").text
                except:
                    email = None

                faculty_data.append({
                    "serial_id": serial_id,
                    "photo": photo_url,
                    "name": name,
                    "title": title,
                    "email": email,
                })

            try:
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "fsNextPageLink")))
                next_button = driver.find_element(By.CLASS_NAME, "fsNextPageLink")
                next_button.click()
                print("Clicked next page")
            except:
                print("Ending scrape")
                scraping = False

        with open(FACULTY_LIST, "w") as f:
            json.dump(faculty_data, f, indent=4)

if __name__ == "__main__":
    #scrape_faculty()
    with open(FACULTY_LIST, "r") as f:
        faculty_data = json.load(f)
    #save_faculty_images(faculty_data)
    img = Image.open("static/faculty_images/1.jpg")
    width, height = img.size
    print(width, height)
