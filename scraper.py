import time
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from config import ALLOWED_ELEMENT_TYPES, ICON_COLOR_MAP
from utils import reformat_scraped_data
from webdriver_manager.chrome import ChromeDriverManager


def scrape(query: str, output_prefix: str):

    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By

        driver = webdriver.Chrome()
    except:
        print("AF: No Chrome webdriver installed")
        driver = webdriver.Chrome(ChromeDriverManager().install())

    driver.get(f"https://www.forexfactory.com/calendar?month={query}")
    table = driver.find_element(By.CLASS_NAME, "calendar__table")

    data = []
    # Scroll down to the end of the page
    while True:
        # Record the current scroll position
        before_scroll = driver.execute_script("return window.pageYOffset;")

        # Scroll down a fixed amount
        driver.execute_script("window.scrollTo(0, window.pageYOffset + 500);")

        # Wait for a short moment to allow content to load
        time.sleep(2)

        # Record the new scroll position
        after_scroll = driver.execute_script("return window.pageYOffset;")

        # If the scroll position hasn't changed, we've reached the end of the page
        if before_scroll == after_scroll:
            break

    # Now that we've scrolled to the end, collect the data
    for row in table.find_elements(By.TAG_NAME, "tr"):
        row_data = []
        for element in row.find_elements(By.TAG_NAME, "td"):
            class_name = element.get_attribute("class")
            if class_name in ALLOWED_ELEMENT_TYPES:
                if element.text:
                    row_data.append(element.text)
                elif "calendar__impact" in class_name:
                    impact_elements = element.find_elements(By.TAG_NAME, "span")
                    for impact in impact_elements:
                        impact_class = impact.get_attribute("class")
                        color = ICON_COLOR_MAP[impact_class]
                    if color:
                        row_data.append(color)
                    else:
                        row_data.append("impact")

        if len(row_data):
            data.append(row_data)

    reformat_scraped_data(data, output_prefix)

    driver.quit()


if __name__ == "__main__":
    cur_month_date: date = date.today()
    next_month_date: date = cur_month_date + relativedelta(months=1)

    cur_month_query_str: str = (
        f"{cur_month_date.strftime('%b').lower()}.{cur_month_date.year}"
    )
    next_month_query_str: str = (
        f"{next_month_date.strftime('%b').lower()}.{next_month_date.year}"
    )

    scrape(cur_month_query_str, f"current_month_{cur_month_date.year}")
    scrape(next_month_query_str, f"next_month_{next_month_date.year}")
