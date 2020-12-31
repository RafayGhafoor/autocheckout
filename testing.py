import requests
import bs4
from lxml import html
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains

from copy import deepcopy
import time
import selenium
from selenium.webdriver.common.keys import Keys


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

    def check_name(self):
        cart_button = [
            i
            for i in self.soup.findAll("button", attrs={"name": "add"})
            if "add" in i.attrs.values() or "cart" in i.attrs.values()
        ]
        if not cart_button:
            cart_button = self.soup.find("input", attrs={"name": "add"})
        return cart_button

    def check_type(self):
        cart_button = self.soup.find("button", attrs={"type": "submit"})
        if not cart_button:
            cart_button = self.soup.find("input", attrs={"type": "submit"})
        return cart_button

    # def find_add_button(self):
    #     cart_button = self.check_name()
    #     if not cart_button:
    #         cart_button = self.check_type()
    #     if not cart_button:
    #         print(self.url, cart_button)
    #         return -1
    #     else:
    #         return cart_button
    def find_add_button(self):
        _type = "button"

        def find_by_type(_type):
            for i in self.soup.findAll(_type):
                info = list(i.attrs.values())
                info = "".join(list(flatten_list(info))).lower()
                if "submit" in info and "checkout" not in info:
                    return {
                        "id": i.attrs.get("id"),
                        "class": " ".join(i.attrs.get("class")),
                        "xpath": self.xpath_soup(i),
                    }
                elif (
                    "add" in info
                    or "cart" in info
                    and "close" not in info
                    and "checkout" not in info
                ):
                    return {
                        "id": i.attrs.get("id"),
                        "class": " ".join(i.attrs.get("class")),
                        "xpath": self.xpath_soup(i),
                    }
                    # return

        cart_xpath = find_by_type("button")
        if not cart_xpath:
            cart_xpath = find_by_type("input")
            print(cart_xpath)
        return cart_xpath

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


urls = [
    "https://shop.bellabeat.com/products/leaf-urban",
    "https://www.biotrust.com/products/biotrust-pro-x10-best-probiotic-supplement",
    "https://www.bhcosmetics.com/products/zodiac-love-signs",
    "https://www.gaiam.com/products/95-1407",
]

driver = webdriver.Chrome(ChromeDriverManager().install())
for url in urls:
    driver.get(url)
    time.sleep(5)
    # soup = html.fromstring(driver.page_source)
    # tree = soup.getroottree()
    # print(tree)
    # result = soup.xpath('//*[. = "XML"]')
    # for r in result:
    # print(tree.getpath(r))
    soup = bs4.BeautifulSoup(driver.page_source, "lxml")

    cart_obj = AddToCart(url, soup)
    add_to_cart_button = cart_obj.find_add_button()
    _get = lambda x: add_to_cart_button.get(x)
    _id, _class, _xpath = _get("id"), _get("class"), _get("xpath")
    element = driver.find_elements_by_xpath(f"//button")
    if not element:
        element = driver.find_elements_by_xpath(f"//input")
    for i in element:

        if i.get_attribute("class") == _class or 'add' in i.get_attribute("class"):
            try:
                i.click()
                time.sleep(3)
                print("CLICKED")
            except Exception as e:
                print(e)
                continue
        elif i.get_attribute("id") == _id:
            try:
                i.click()
                time.sleep(3)
                print("CLICKED")
            except Exception as e:
                print(e)
                continue
    # element.click()
    # print("Element is visible? " + str(element.is_displayed()))
    # driver.implicitly_wait(10)
    # element.click()
    # element = driver.find_element_by_xpath(_xpath)

    # driver.implicitly_wait(10)
    # actions.move_to_element(element)
    # actions.double_click(element)
    # actions.perform()
    # https://stackoverflow.com/questions/44119081/how-do-you-fix-the-element-not-interactable-exception
