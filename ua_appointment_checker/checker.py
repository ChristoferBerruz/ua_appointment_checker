import time
from loguru import logger
from dataclasses import dataclass
from selenium import webdriver
from bs4 import BeautifulSoup
from typing import Callable, List
from selenium.webdriver.common.by import By
import functools
import contextlib


def are_appointments_available(
        web_driver: webdriver.Remote,
        target_url: str,
        load_page_wait_seconds: int = 10
) -> bool:
    """Returns whether there are appointments available by making a GET
    Request to the target_url using a web_driver and asserting state
    on the html page.

    Args:
        web_driver (webdriver.Remote): the webdriver to us
        target_url (str): which url to check
        load_page_wait_seconds (int, optional): how long to wait for the url to load.
            Defaults to 10 seconds.

    Returns:
        bool: _description_
    """
    logger.info(f"Getting html page from url: {target_url!r}")
    web_driver.get(target_url)
    logger.info(f"Sleeping {load_page_wait_seconds} seconds to load html")
    time.sleep(load_page_wait_seconds)
    page_html = web_driver.page_source
    logger.info(f"Extracting and parsing html")
    bsoup = BeautifulSoup(page_html, "html.parser")
    target_string = "Немає вільних місць"
    logger.info(f"Checking if {target_string!r} is in html page.")
    return target_string not in bsoup.text


@dataclass
class AppointmentsAvailable:
    date: str
    number_of_appointments: int

    @classmethod
    def from_bsoup(cls, bsoup: BeautifulSoup) -> "AppointmentsAvailable":
        # timeslots are timezone aware, whatever that timezone is
        timeslots = [
            item.text for item in bsoup.find_all("li")
        ]
        # This is rendered directly from the HTML website
        date_of_slots = bsoup.find(id="heading-slot-date").text
        return cls(date=date_of_slots, number_of_appointments=len(timeslots))


def get_appointments_available(
        driver: webdriver.Remote,
        target_url: str,
        initial_load_page_time_seconds: int = 10,
        wait_time_after_clicking_buttons: int = 10
) -> List[AppointmentsAvailable]:
    """Get the appointments available in the target url

    Args:
        driver (webdriver.Remote): the driver, or browser, to use.
        target_url (str): the url to load and manipulate
        initial_load_page_time_seconds (int, optional): How many
            seconds to wait after getting the initial page. Defaults to 10.
        wait_time_after_clicking_buttons (int, optional): How many
            seconds to wait after clicking each date button. Defaults to 10.

    Returns:
        List[AppointmentsAvailable]: Appointments available information
    """
    logger.info(f"Generating appointment information for url: {target_url!r}")
    logger.debug(
        f"Initial load page for {target_url!r}. Sleeping for {initial_load_page_time_seconds} seconds.")
    driver.get(target_url)
    time.sleep(initial_load_page_time_seconds)
    all_day_buttons = driver.find_elements(By.NAME, 'day')
    buttons_with_appointments = [
        button for button in all_day_buttons if button.get_attribute("disabled") is None
    ]
    # Some buttons have the "selected" added to their label
    # Let's just remove them to leave it as a date.

    def _get_date_from_button(button):
        return button.get_attribute("aria-label").replace("selected", "").strip()

    button_labels = [
        _get_date_from_button(button) for button in buttons_with_appointments
    ]
    logger.debug(
        f"Found {len(buttons_with_appointments)} dates that have appointments: {button_labels}")
    result = []
    # NOTE: Something interesting happens here.
    # The webdriver is local, which means that objects are short lived
    # and disappear after a refresh. As a result, we can't just
    # iterate over the button objects (as they are ephemeral as well)
    # and click them. Why? Because each click triggers a refresh of the page
    # invalidating the objects.
    for label in set(button_labels):
        logger.debug(f"Finding appointment information for date {label!r}")
        buttons_to_search = driver.find_elements(By.NAME, 'day')
        matching_buttons = [
            button for button in buttons_to_search if _get_date_from_button(button) == label]
        if not matching_buttons:
            logger.debug(f"No buttons found for date: {label!r}")
            continue
        target_button = matching_buttons[0]
        logger.debug(
            f"Clicking button and sleep for {wait_time_after_clicking_buttons} seconds")
        target_button.click()
        time.sleep(wait_time_after_clicking_buttons)
        page_html = driver.page_source
        bsoup = BeautifulSoup(page_html, "html.parser")
        # The date here will be whatever date is parsed by the appointments
        # from the HTML. In my experiments, it is context aware
        # of whatever language is set. As a result, the dates are in
        # Ukrainian.
        result.append(AppointmentsAvailable.from_bsoup(bsoup))
    return result


def args_memo(func: Callable):
    memory = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if args not in memory:
            logger.debug(
                f"{args} not found in memory. Computing function: {func.__name__!r}")
            res = func(*args, **kwargs)
            memory[args] = res
        logger.debug(f"Returning cached value for {args}")
        return memory[args]
    return wrapper


@contextlib.contextmanager
def get_default_remote_webdriver(remote_url: str) -> webdriver.Remote:
    """Returns a Google Chrome Remote Web Driver

    Args:
        remote_url (str): the remote url

    Returns:
        webdriver.Remote: the webdriver
    """
    # TODO: Currently, the webdriver can only handle one connection at a time
    # That's okay for a low-threaded, low requests environment. However,
    # we need a way to "await" for the webdriver to be done
    # if it is running a command.
    try:
        driver = webdriver.Remote(
            remote_url, options=webdriver.ChromeOptions())
        yield driver
    finally:
        driver.quit()
