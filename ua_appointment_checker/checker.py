import time
from loguru import logger
from selenium import webdriver
from bs4 import BeautifulSoup
from typing import Callable
import functools


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


@args_memo
def get_default_remote_webdriver(remote_url: str) -> webdriver.Remote:
    """Returns a Google Chrome Remote Web Driver

    Args:
        remote_url (str): the remote url

    Returns:
        webdriver.Remote: the webdriver
    """
    return webdriver.Remote(remote_url, options=webdriver.ChromeOptions())
