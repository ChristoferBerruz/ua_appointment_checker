from selenium import webdriver
import click
from bs4 import BeautifulSoup
import time

from loguru import logger

embassy_url = "https://consulategeneralofukraineinsanfrancisco.setmore.com/beta/services/43f35be4-5432-4289-b1b0-3838ab21d825?step=time-slot&products=43f35be4-5432-4289-b1b0-3838ab21d825&type=service&staff=5P8eQv743liUR3eBhDkLo1fP4Vdbtmtq&staffSelected=false"


@click.command()
@click.option("--load-page-wait-seconds", default=30, type=int, help="How many seconds to wait for the page to fully load")
@click.option("--remote-chrome-driver-url", default="http://localhost:4444/wd/hub", type=str, help="The chrome url docker container to invoke the Selenium web driver.")
@click.option("--embassy-url", type=str, default=embassy_url, help="The embassy appointment url to check")
def watch(load_page_wait_seconds: int, remote_chrome_driver_url: str, embassy_url: str):
    logger.info(
        f"Initializing webdrive using url: {remote_chrome_driver_url!r}")
    driver = webdriver.Remote(remote_chrome_driver_url,
                              options=webdriver.ChromeOptions())
    target_string = "Немає вільних місць"
    logger.info(
        f"Making GET request using webdriver for url: {embassy_url!r}")
    driver.get(embassy_url)
    logger.info(
        f"Sleeping for {load_page_wait_seconds} seconds to load page")
    time.sleep(load_page_wait_seconds)
    logger.info(f"Extracting and parsing html")
    page_html = driver.page_source
    bsoup = BeautifulSoup(page_html, "html.parser")
    if target_string not in bsoup.text:
        logger.info("Appointments available. Sending mail")
        pass
    else:
        # print that no appointment available
        logger.info("No appointments available.")
    logger.info("Done.")


def main():
    watch()
