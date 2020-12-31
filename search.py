import random
import bs4
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import os
import sys

driver = webdriver.Chrome(ChromeDriverManager().install())

search_term = "inurl:products intext:review intext:buy site:"


def duckduckgo_search(url):
    url = f"https://duckduckgo.com/html/?q={search_term}{url}"
    driver.get(url)
    soup = bs4.BeautifulSoup(driver.page_source, "lxml")

    search_content = soup.find("div", attrs={"id": "result"})
    try:
        content = [i.get("href") for i in search_content.findAll("a") if i.get("href")]
        for i in content:
            if "-" in i:
                print(i)
                return i
    except:
        return ""


def chrome_search(url):
    url = f"https://google.com/search?q={search_term}{url}"
    driver.get(url)
    soup = bs4.BeautifulSoup(driver.page_source, "lxml")
    if "our systems have detected unusual traffic" in soup.prettify().lower():
        sys.exit("Rate Limit Exceeded. Exiting...")
    search_content = soup.find("div", attrs={"id": "search"})
    try:
        content = [i.get("href") for i in search_content.findAll("a") if i.get("href")]
        for i in content:
            if "-" in i and "blog" not in i:
                return i
    except:
        return ""


def main():

    with open("list.txt", "r") as f:
        links = f.readlines()
        links = [f"http://{i.strip()}" for i in links if len(i) > 5]
        with open("products.txt", "a") as f:
            try:
                for url in links:
                    content = chrome_search(url)
                    if content and "google" not in content:
                        f.write(content + "\n")
                    print(f"{url} Scraped")
            except Exception as e:
                print(e)


if __name__ == "__main__":
    main()