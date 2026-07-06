import os
import json
import time
from dataclasses import dataclass

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager


@dataclass
class Result:
    success: bool
    error: str | None = None


def get_driver(headless: bool) -> WebDriver:
    service = Service(GeckoDriverManager().install())

    options = webdriver.FirefoxOptions()
    options.set_preference("intl.accept_languages", "en-US,en")
    options.add_argument("-private-window")

    if headless:
        options.add_argument("--headless")

    driver = webdriver.Firefox(service=service, options=options)

    return driver


def sing_in(driver: WebDriver, timeout: int) -> None:
    wait = WebDriverWait(driver, timeout)

    wait.until(ec.visibility_of_element_located(
        (By.XPATH, '//a[@id="hs-eu-decline-button"]'))).click()
    time.sleep(2)

    input_user = wait.until(ec.visibility_of_element_located(
        (By.XPATH, '//input[@data-testid="login-form--username"]')))
    input_user.click()
    input_user.send_keys(os.environ["USER_MAIL"])
    time.sleep(1.5)

    input_password = wait.until(ec.visibility_of_element_located(
        (By.XPATH, '//input[@data-testid="login-form--password"]')))
    input_password.click()
    input_password.send_keys(os.environ["USER_PASSWORD"])
    time.sleep(1.5)

    wait.until(ec.visibility_of_element_located(
        (By.XPATH, '//button[@data-testid="login-form--button-login" and normalize-space()="SIGN IN"]'))).click()

    wait.until(ec.visibility_of_element_located(
        (By.XPATH, '//div[@id="main-dashboard"]')))

    return


def select_hotel_(driver: WebDriver, timeout: int, hotel_name: str) -> None:
    wait = WebDriverWait(driver, timeout)

    wait.until(ec.invisibility_of_element_located(
        (By.CSS_SELECTOR, ".el-loading-mask")))

    wait.until(ec.visibility_of_element_located(
        (By.XPATH, '//div[@class="topbar__hotel-search"]'))).click()

    wait.until(ec.visibility_of_element_located(
        (By.XPATH, f'//div[contains(@class, "hotel-search__results__item__name")'
                   f'and normalize-space()="{hotel_name}"]'))).click()
    time.sleep(2)

    wait.until(ec.visibility_of_element_located(
        (By.XPATH, f'//div[contains(@class, "topbar__hotel-search__name__text el-tooltip__trigger '
                   f'el-tooltip__trigger") and normalize-space()="{hotel_name}"]')))

    return


def scraping(headless: bool, timeout: int, push_list: list[dict]) -> None:
    if push_list:
        driver = get_driver(headless)
        driver.get(f"{os.environ["BASE_URL"]}/login")

        sing_in(driver, timeout)

        for push in push_list:
            select_hotel_(driver, timeout, push['hotel_name'])

    return


def main(headless: bool = True, timeout: int = 60) -> Result:
    load_dotenv()

    # Cambiaremos
    with open('payload.json', 'r', encoding='utf-8') as file:
        push_list = json.load(file)

    scraping(headless, timeout, push_list)

    return Result(success=True, error=None)


if __name__ == '__main__':
    main(headless=False)