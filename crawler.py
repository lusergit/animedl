#!/bin/env python3
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import logging
import urllib.request
import progressbar

# progress bar
pbar = None

def show_progress(block_num, block_size, total_size):
    global pbar
    if pbar is None:
        pbar = progressbar.ProgressBar(maxval=total_size)
        pbar.start()

    downloaded = block_num * block_size
    if downloaded < total_size:
        pbar.update(downloaded)
    else:
        pbar.finish()
        pbar = None

# driver handling
def init_driver():
    options = Options()
    options.add_argument("-headless")
    
    driver = webdriver.Firefox(options=options)
    logging.info("Init driver")
    return driver

def deinit_driver(driver):
    logging.info("Deinit driver")
    driver.quit()
        
# driver operations
def get_frame_link_of(url, driver):
    to_ret = None
    try:
        # Navigate to the desired web page
        driver.get(url)

        logging.info("Waiting for element with id embed")
        # wait for element with id "embed to be rendered"
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "embed"))
        )
        if element:
            to_ret = element.get_attribute("src")
            logging.info("Found frame with link {}".format(to_ret))
        else:
            logging.warning("Not found!")
    finally:
        # Close the browser
        return to_ret

def download_from_frame(url, name):
    import requests
    r = requests.get(url)
    for line in r.text.splitlines():
        if "window.downloadUrl" in line:
            link = line.replace("window.downloadUrl = '", "").replace("'", "").strip()
            urllib.request.urlretrieve(link, name, show_progress)

# Main
def main():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    if len(sys.argv) < 2:
        print("usage: ", sys.argv[0], " [URL]")
        exit(1)
    url = sys.argv[1]
    name = sys.argv[2]
    driver = init_driver()
    frame_link = get_frame_link_of(url, driver)
    deinit_driver(driver) 
    logging.info("Downloading...")
    download_from_frame(frame_link, name)
    logging.info("Done.")

if __name__ == "__main__":
    main()
