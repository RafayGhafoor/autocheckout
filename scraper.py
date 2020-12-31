import json
import bs4
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import csv
from copy import deepcopy
import time
import selenium
from selenium.webdriver.common.keys import Keys
import os
from urllib.parse import urlsplit
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument("--disable-logging")
driver = webdriver.Chrome(
    ChromeDriverManager().install(), options=options, service_log_path="NUL"
)
driver.set_page_load_timeout(10)


with open("info.json", "r") as f:
    data = json.load(f)


def get_base_url(url):
    base_url = "{0.scheme}://{0.netloc}/".format(urlsplit(url))
    return base_url


def click(element, delay=0.5):
    tries = 3
    for i in range(tries):
        try:
            element.click()
            break
        except selenium.common.exceptions.ElementClickInterceptedException:
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            driver.execute_script("window.scrollTo(0, 400);")
        except selenium.common.exceptions.StaleElementReferenceException:
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            driver.execute_script("window.scrollTo(0, 400);")
        except selenium.common.exceptions.ElementNotInteractableException:
            pass
        except selenium.common.exceptions.NoSuchElementException:
            pass
        finally:
            time.sleep(delay)


def flatten_list(nested_list):
    """Flatten an arbitrarily nested list, without recursion (to avoid
    stack overflows). Returns a new list, the original list is unchanged.
    >> list(flatten_list([1, 2, 3, [4], [], [[[[[[[[[5]]]]]]]]]]))
    [1, 2, 3, 4, 5]
    >> list(flatten_list([[1, 2], 3]))
    [1, 2, 3]
    """
    nested_list = deepcopy(nested_list)

    while nested_list:
        sublist = nested_list.pop(0)

        if isinstance(sublist, list):
            nested_list = sublist + nested_list
        else:
            yield sublist


class AddToCart:
    def __init__(self, url, soup):
        self.url = url
        self.soup = soup

    def find_add_button(self):
        _type = "button"

        def find_by_type(_type):
            for i in self.soup.findAll(_type):
                info = list(i.attrs.values())
                info = "".join(list(flatten_list(info))).lower()
                if "add" in info or "cart" in info and "close" not in info:
                    return {
                        "id": i.attrs.get("id"),
                        "class": " ".join(i.attrs.get("class")),
                        "xpath": self.xpath_soup(i),
                    }

        cart_info = find_by_type("button")
        if not cart_info:
            cart_info = find_by_type("input")
        return cart_info

    def xpath_soup(self, element):
        # type: (typing.Union[bs4.element.Tag, bs4.element.NavigableString]) -> str
        """
        Generate xpath from BeautifulSoup4 element.
        :param element: BeautifulSoup4 element.
        :type element: bs4.element.Tag or bs4.element.NavigableString
        :return: xpath as string
        :rtype: str
        Usage
        -----
        >>> import bs4
        >>> html = (
        ...     '<html><head><title>title</title></head>'
        ...     '<body><p>p <i>1</i></p><p>p <i>2</i></p></body></html>'
        ...     )
        >>> soup = bs4.BeautifulSoup(html, 'html.parser')
        >>> xpath_soup(soup.html.body.p.i)
        '/html/body/p[1]/i'
        >>> import bs4
        >>> xml = '<doc><elm/><elm/></doc>'
        >>> soup = bs4.BeautifulSoup(xml, 'lxml-xml')
        >>> xpath_soup(soup.doc.elm.next_sibling)
        '/doc/elm[2]'
        """
        components = []
        child = element if element.name else element.parent
        for parent in child.parents:  # type: bs4.element.Tag
            siblings = parent.find_all(child.name, recursive=False)
            components.append(
                child.name
                if 1 == len(siblings)
                else "%s[%d]"
                % (child.name, next(i for i, s in enumerate(siblings, 1) if s is child))
            )
            child = parent
        components.reverse()
        return "/%s" % "/".join(components)


def get_urls(filename="products.txt"):
    with open(filename, "r") as f:
        return list(
            set(
                [
                    i.strip().replace("\n", "")
                    for i in f.readlines()
                    if i.strip().replace("\n", "")
                ]
            )
        )


def click_checkout(driver, url):
    driver.get(get_base_url(url) + "cart")
    driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'r')
    driver.refresh()
    element = driver.find_elements_by_xpath(f"//button")
    if not element:
        element = driver.find_elements_by_xpath(f"//input")
    elif element:
        input_elements = driver.find_elements_by_xpath(f"//input")
        if input_elements:
            element.extend(input_elements)

    for i in element:
        try:
            if i.text.lower() == "checkout":
                i.click()
            if "checkout" in i.get_attribute(
                "class"
            ).lower() and "submit" in i.get_attribute("type"):
                click(i)
            if "checkout" in i.get_attribute("class").lower():
                click(i)
            if "checkout" in i.get_attribute("id").lower():
                click(i)
            if "submit" in i.get_attribute("type") and "checkout" in i.get_attribute(
                "name"
            ):
                click(i)
        except Exception as e:
            print(e)
            continue


def fill_information(driver, soup):
    for i in soup.findAll("input"):
        if not i.attrs.get("name"):
            continue
        if "checkout" in i.attrs.get("name"):
            for k, v in data.items():
                if k in i.attrs.get("name").replace("checkout[shipping_address]", ""):
                    try:
                        elements = driver.find_elements_by_name(i.attrs.get("name"))
                        for element in elements:
                            try:
                                element.clear()
                                element.send_keys(v)
                                break
                            except:
                                continue
                    except:
                        pass


def click_add_to_cart(driver, urls):
    if os.path.exists("report.csv"):
        os.remove("report.csv")

    with open("report.csv", "a", newline="") as file:
        fieldnames = ["URL", "Status"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for url in urls:
            url_status = True
            url = url.strip()
            try:
                driver.get(url.strip())
                driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'r')
                driver.refresh()
            except Exception as e:
                writer.writerow({"URL": url, "Status": "Incomplete"})
                
            # driver.execute_script("window.scrollTo(0, 400);")
            soup = bs4.BeautifulSoup(driver.page_source, "lxml")
            cart_obj = AddToCart(url, soup)
            add_to_cart_button = cart_obj.find_add_button()
            if not add_to_cart_button:
                writer.writerow({"URL": url, "Status": "Incomplete"})
                print(f"Cart button for {url} not found.")
                url_status = False
                continue

            message = f"\n{url}->"
            status = "incomplete"
            try:
                webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                _get = lambda x: add_to_cart_button.get(x)
                _id, _class, _xpath = _get("id"), _get("class"), _get("xpath")
                element = driver.find_elements_by_xpath(f"//button")
                if not element:
                    element = driver.find_elements_by_xpath(f"//input")
                elif element:
                    element.extend(driver.find_elements_by_xpath(f"//input"))

                is_clicked = False

                for i in element:
                    try:
                        if (
                            i.get_attribute("class") == _class
                            or "add" in i.get_attribute("class").lower()
                        ):
                            click(i)
                            is_clicked = True
                        elif i.get_attribute("id") == _id:
                            click(i)
                            is_clicked = True
                        elif 'add' in i.get_attribute('name') and 'submit' in i.get_attribute('type'):
                            click(i)
                        
                    except Exception as e:
                        print("Add to cart: ", e)
                        continue

                if is_clicked:
                    click_checkout(driver, url)
                    soup = bs4.BeautifulSoup(driver.page_source, "lxml")
                    fill_information(driver, soup)
                    try:
                        element = driver.find_element_by_id("continue_button")
                        if not element:
                            element = driver.find_element_by_id("checkout")
                        click(element)

                    except Exception as e:
                        print("Add to cart: ", e)
                        url_status = False
                else:
                    url_status = False
                    print("NOT CLICKED")

            except Exception as e:
                print(e)
            finally:
                write_status = "Complete" if url_status else "Incomplete"
                writer.writerow({"URL": url, "Status": write_status})


def main():

    urls = get_urls()
    # urls = [
    #     "https://www.biotrust.com/products/biotrust-ageless-multi-collagen-protein-powder"
    # ]
    click_add_to_cart(driver, urls)


main()
