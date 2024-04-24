from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.wait import WebDriverWait


def create_new_driver() -> WebDriver:
    options = webdriver.FirefoxOptions()

    SHOW = False
    if not SHOW:
        options.add_argument("-headless")

    new_driver = webdriver.Firefox(options=options)
    return new_driver


if __name__ == '__main__':
    driver = create_new_driver()
    url = 'https://yandex.ru/maps/?mode=routes&routes[timeDependent][time]=2024-04-25T11%3A00%3A00&rtext=45.055403%2C39.048050~45.057861%2C39.034099&rtt=auto'
    driver.get(url)

    res_time = driver.find_element(By.CLASS_NAME, "auto-route-snippet-view__route-duration").text
    res_dist = driver.find_element(By.CLASS_NAME, "auto-route-snippet-view__route-subtitle").text
    print(res_time)
    print(res_dist)
