import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
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


def select_hotel(driver: WebDriver, timeout: int, hotel_name: str) -> None:
    time.sleep(2)
    wait = WebDriverWait(driver, timeout)

    wait.until(ec.invisibility_of_element_located(
        (By.CSS_SELECTOR, ".el-loading-mask is-fullscreen")))

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

def calculate_click_date(target_date_str: str) -> str:
    target_date = datetime.strptime(target_date_str, "%Y-%m-%d")

    target_day_of_week = target_date.weekday()

    today = datetime.now()

    current_monday = today - timedelta(days=today.weekday())

    column_date = current_monday + timedelta(days=target_day_of_week)

    return column_date.strftime("%Y-%m-%d")



def change_int(driver: WebDriver, element: WebElement, value: str) -> None:
    driver.execute_script(
        "arguments[0].value = arguments[1]; "
        "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));"
        "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
        element, value)

    return


def create_push(driver: WebDriver, timeout: int, push: dict) -> None:
    time.sleep(2)
    wait = WebDriverWait(driver, timeout)

    wait.until(ec.invisibility_of_element_located(
        (By.CSS_SELECTOR, ".el-loading-mask is-fullscreen")))

    wait.until(ec.visibility_of_element_located(
        (By.XPATH, f'//div[contains(@class, "d{calculate_click_date(push['star_date'])}")]'))).click()

    internal_name = wait.until(ec.visibility_of_element_located(
        (By.XPATH, '//input[@placeholder="Internal name"]')))
    internal_name.send_keys(push['internal_name'])
    time.sleep(1.5)

    send_time = wait.until(ec.visibility_of_element_located(
        (By.XPATH, f'//input[@placeholder="Select min"]')))
    change_int(driver, send_time, push['send_time'])
    wait.until(ec.visibility_of_element_located(
        (By.XPATH, '//button[@class="el-time-panel__btn confirm"]'))).click()

    end_date = wait.until(ec.visibility_of_element_located(
        (By.XPATH, '//input[@placeholder="End"]')))
    change_int(driver, end_date, push['end_date'])
    strat_date = wait.until(ec.visibility_of_element_located(
        (By.XPATH, '//input[@placeholder="Start"]')))
    change_int(driver, strat_date, push['star_date'])

    wait.until(ec.visibility_of_element_located(
        (By.XPATH, '//div[@class="image-library-button"]'))).click()
    wait.until(ec.visibility_of_element_located(
        (By.XPATH, f'//div[contains(@class, "title") and normalize-space()="{push['img']}"]'))).click()
    wait.until(ec.visibility_of_element_located(
        (By.XPATH, '//button[@class="el-button el-button--primary el-button--default '
                   'is-round brand-button right"]'))).click()

    title = wait.until(ec.visibility_of_element_located(
        (By.XPATH, '//input[@placeholder="Enter title"]')))
    title.send_keys(push['title'])
    time.sleep(1.5)

    message_content = wait.until(ec.visibility_of_element_located(
        (By.XPATH, '//textarea[@placeholder="Enter message"]')))
    message_content.send_keys(push['message_content'])
    time.sleep(2)

    wait.until(ec.visibility_of_element_located(
        (By.XPATH, '//div[@class="el-select__selected-item el-select__placeholder is-transparent"]'))).click()
    wait.until(ec.element_to_be_clickable(
        (By.XPATH, '//li[@role="option" and .//span[normalize-space()="External website link"]]'))).click()

    url = wait.until(ec.visibility_of_element_located(
        (By.XPATH, '//div[@class="el-input el-input--large el-input-group el-input-group--prepend"]'
                   '//div[@class="el-input__wrapper"]'
                   '//input[@class="el-input__inner"]')))
    url.send_keys(push['url'])

    wait.until(ec.visibility_of_element_located(
        (By.XPATH, '//label[@class="el-checkbox el-checkbox--large alerts-basic-info__url-checkbox"]'))).click()

    button_text = wait.until(ec.visibility_of_element_located(
        (By.XPATH, '//input[@placeholder="View more"]')))
    button_text.send_keys(push['button_text'])
    time.sleep(1.5)

    wait.until(ec.visibility_of_element_located(
        (By.XPATH, '//button[contains(@class, "brand-button") and .//span[text()="Save"]]'))).click()
    time.sleep(2)

    return


def scraping(headless: bool, timeout: int, push_list: list[dict]) -> None:
    if push_list:
        driver = get_driver(headless)
        driver.get(f"{os.environ["BASE_URL"]}/login")

        sing_in(driver, timeout)

        for push in push_list:
            select_hotel(driver, timeout, push['hotel_name'])

            driver.get(f"{os.environ["BASE_URL"]}/crm/alerts/configuration")

            create_push(driver, timeout, push)

            driver.get(f"{os.environ["BASE_URL"]}/dashboard/main")

        driver.quit()

    return


def main(headless: bool = True, timeout: int = 60) -> Result:
    load_dotenv()

    # Cambiaremos
    with open('payload.json', 'r', encoding='utf-8') as file:
        push_list = json.load(file)

    scraping(headless, timeout, push_list)

    return Result(success=True, error=None)


if __name__ == '__main__':
    main()