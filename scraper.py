import time
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from config import ALLOWED_ELEMENT_TYPES, ICON_COLOR_MAP
from utils import reformat_scraped_data
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def scrape(query: str, output_prefix: str, driver):
    try:
        # Load the calendar page
        driver.get(f"https://www.forexfactory.com/calendar?month={query}")

        # Wait for the calendar table to be present
        wait = WebDriverWait(driver, 30)
        table = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "calendar__table"))
        )

        # Initialize a list to store scraped data
        data = []

        # Scroll until the bottom of the page is reached
        while True:
            # Record the current scroll position
            before_scroll = driver.execute_script("return window.pageYOffset;")

            # Scroll down by a fixed amount
            driver.execute_script("window.scrollTo(0, window.pageYOffset + 500);")

            # Wait for new content to load (use WebDriverWait to check changes)
            wait.until(
                lambda d: driver.execute_script("return window.pageYOffset;")
                != before_scroll
            )

            # Record the new scroll position
            after_scroll = driver.execute_script("return window.pageYOffset;")

            # Break if no further scrolling is possible
            if before_scroll == after_scroll:
                break

        # Collect data from the table rows
        for row in table.find_elements(By.TAG_NAME, "tr"):
            row_data = []
            for element in row.find_elements(By.TAG_NAME, "td"):
                class_name = element.get_attribute("class")
                if class_name in ALLOWED_ELEMENT_TYPES:
                    if element.text:
                        row_data.append(element.text)
                    elif "calendar__impact" in class_name:
                        # Handle impact icons
                        impact_elements = element.find_elements(By.TAG_NAME, "span")
                        for impact in impact_elements:
                            impact_class = impact.get_attribute("class")
                            color = ICON_COLOR_MAP.get(impact_class, "impact")
                            row_data.append(color)
                        else:
                            row_data.append("impact")

            if row_data:  # Add non-empty rows to data
                data.append(row_data)

        # Reformat the scraped data and save
        reformat_scraped_data(data, output_prefix)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Ensure the driver is closed even if an error occurs
        driver.quit()


if __name__ == "__main__":

    from selenium import webdriver
    from selenium.webdriver.common.by import By

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.binary_location = (
        "chrome-linux64/chrome-linux64/chrome"  # Adjust the path
    )

    driver = webdriver.Chrome(
        service=Service("bin/chromedriver"), options=chrome_options
    )

    scrape("current", "current_month", driver)
    scrape("next", "next_month", driver)
