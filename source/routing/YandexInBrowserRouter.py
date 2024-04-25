from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.by import By

from yandex_in_browser_routing_tools import insert_data
from time import sleep


def create_new_driver(show=False) -> WebDriver:
    options = webdriver.FirefoxOptions()

    if not show:
        options.add_argument("-headless")

    new_driver = webdriver.Firefox(options=options)
    return new_driver


class YandexInBrowserRouter:
    def __init__(self):
        self.driver = create_new_driver()

    def parse_urls(self, urls):
        for url, date, t, segment_id in urls:
            self.driver.get(url)
            time = self.driver.find_element(By.CLASS_NAME, "auto-route-snippet-view__route-duration").text
            dist = self.driver.find_element(By.CLASS_NAME, "auto-route-snippet-view__route-subtitle").text
            print(time, dist)
            insert_data(segment_id, dist, time, date, t)
            sleep(1)
            

if __name__ == '__main__':
    from source.database.db_init import Segment
    from source.database.db_sessions import get_objects
    from datetime import datetime, timedelta
    from yandex_in_browser_routing_tools import generate_urls_bulk
    segments = get_objects(class_name=Segment)
    dates_list = [(datetime.now() + timedelta(days=1)).date()]
    times_list = [i for i in range(6, 24)]
    urls = generate_urls_bulk(segments, dates_list, times_list)
    print(urls)
