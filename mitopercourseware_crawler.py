from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import math
import time

# ============ DB SETTING ===============
import pymongo
from pymongo import MongoClient
import certifi

CONNECTION_STRING = "mongodb+srv://admin:M1dJJldNVSE6mjSo@moodlerec.w2j6m9t.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())
dbname = client['moodlerec']
collection = dbname['mitopencourseware']
# ============ DB SETTING END ===============


# configure webdriver
options = Options()
options.add_argument('--headless')  # hide GUI
options.add_argument("--window-size=1920,1080")  # set window size to native GUI size
options.add_argument("start-maximized")  # ensure window is full-screen

...
# configure chrome browser to not load images and javascript
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option(
    # this will disable image loading
    "prefs", {"profile.managed_default_content_settings.images": 2}
)

driver = webdriver.Chrome(options=options, chrome_options=chrome_options)
# driver2 = webdriver.Chrome(options=options, chrome_options=chrome_options)
driver.get("https://ocw.mit.edu/search/")
element = WebDriverWait(driver=driver, timeout=5).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'article'))
)
total_courses = int(driver.find_element(By.CSS_SELECTOR, ".results-total-number").text)
pages = math.ceil(total_courses/10)
for x in range(pages):
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(3)
#
#
courses_url = []
elems = driver.find_elements(By.XPATH, "//a[@href]")
for elem in elems:
    if "courses" in elem.get_attribute("href"):
        courses_url.append(elem.get_attribute("href"))
courses_url = list(dict.fromkeys(courses_url))
# print(courses_url)

for index, url in enumerate(courses_url):
    driver.get(url)
    time.sleep(2)
    element = WebDriverWait(driver=driver, timeout=5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#course-description'))
    )
    # ========== AUTHORS ==============
    author_elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'course-info-instructor')]")
    authors = []
    for author in author_elements:
        if author.text:
            authors.append(author.text)
    # ========== DEPARTMETS ==============
    department_elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'course-info-department')]")
    departments = []
    for department in department_elements:
        if department.text:
            departments.append(department.text)
    # ========== DESCRIPTION =============
    try:
        desc_element = driver.find_element(By.CSS_SELECTOR, "#full-description")
    except NoSuchElementException:
        try:
            driver.find_element(By.CSS_SELECTOR, "#expand-description").click()
            desc_element = driver.find_element(By.CSS_SELECTOR, "#expanded-description")
        except NoSuchElementException:
            try:
                desc_element = driver.find_element(By.CSS_SELECTOR, "#course-description p:first-child")
            except NoSuchElementException:
                desc_element = driver.find_element(By.CSS_SELECTOR, "#course-description")
                print("=========INSIDE THIRD EXCEPT===========")
                print(desc_element.text)

    # ========== FORMAT ===============
    format_elements = driver.find_elements(By.XPATH, "//div[@class = 'learning-resource-type-item']//span")
    formats = []
    for format in format_elements:
        formats.append(format.text)

    objToSave = {
        "_id": driver.current_url,
        "title": driver.find_element(By.XPATH, "//div[@id = 'course-banner']//a").text,
        "authors": authors,
        "description": desc_element.text.replace(".Show less", "."),
        "Departments": departments,
        "format": formats,
        "lor": "mitopencourseware"
    }
    try:
        collection.insert_one(objToSave)
        print(index, " - ", objToSave)
    except pymongo.errors.DuplicateKeyError:
        print("duplicate")
        continue

driver.quit()
