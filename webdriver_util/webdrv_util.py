import difflib
import os
import random
import re
import traceback
import requests
from time import sleep
from dotenv import load_dotenv
from RPA.Browser.Selenium import Selenium
from Log.logs import Logs
import time
from selenium.common import (ElementClickInterceptedException,
                             ElementNotInteractableException,
                             JavascriptException, 
                             NoSuchElementException, 
                             TimeoutException)
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from helpers.selector import Selector, TagAttVl
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta  


# *This is my personal lib with selenium methods that help me scraper better.
load_dotenv("config\.env")
Timeout = 5
RetryAttempts = 2
logger = Logs.Returnlog(os.getenv("name_app"), "Scrapping")

def parse_time_ago(text)->datetime|None:  
    # Regex to find patterns like "x hours ago" or "y minutes ago"  
    pattern = r"(\d+)\s+(hour|minute)s?\s+ago"  
    match = re.search(pattern, text, re.IGNORECASE)  
      
    if not match:  
        logger.error("Pattern not found in the provided string.")  
        return None
  
    # Extract the number and the time unit  
    value, unit = match.groups()  
    value = int(value)  
      
    # Get the current date and time  
    now = datetime.now()  
      
    # Calculate the new date and time by subtracting the found value  
    if "hour" in unit:  
        result_time = now - timedelta(hours=value)  
    elif "minute" in unit:  
        result_time = now - timedelta(minutes=value)  
    else:  
        raise ValueError("Unrecognized time unit.")  
      
    return result_time  

def wait_for_modal(driver, timeout=15, search_click=True):  
    """  
    Waits for a modal to close.  
    Args:  
        driver: The Selenium WebDriver instance.  
        timeout: The timeout in seconds.  
    Returns:  
        True if the modal was closed, False otherwise.  
    Raises:  
        TimeoutException: If the modal does not close within the specified timeout.  
    """  
    # Scroll down to activate the modal  
    #scroll_down(driver)  
    driver.execute_script("document.body.innerHTML += '';")  
    sleep(0.800)
    logger.info(f"Modal closed.")  
    return True  

 

def extract_names_from_list_items(driver):  
    # Encontre todos os elementos <span> que são filhos de <li> dentro do contexto fornecido  
    spans = driver.driver.find_elements(By.XPATH, "//div[@class='search-filter-menu-wrapper']//li//span")  
      
    # Extraia o texto de cada elemento <span>  
    names = [span.text for span in spans if span.text.strip()] 
      
    return names   

def search_and_click_topics(driver, names: list, target_name):
    best_match_name = find_fuzzy(names, lambda x: x, target_name)    
    if not len(best_match_name.strip())>0: 
        logger.error(f"Topic not found '{target_name}'.")
        return False, True
    else:      
        try:  
            span = find_element(
                driver,
                Selector(xpath= f"//div[@class='search-filter-menu-wrapper']//li//span[text()='{best_match_name}']")
                )
              
            span.click()  
            logger.info(f"Element '{best_match_name}' was clicked.")
            return True, True
        except NoSuchElementException:  
            print(f"Element '{best_match_name}' not found.")  
            return False, False
  
        

def get_free_proxy(source='us_proxy'):  
    """  
    Obtém uma lista de proxies gratuitos da web.  
  
    Args:  
        source (str): A fonte dos proxies ('us_proxy', 'free_proxy_list', 'ssl_proxies').  
  
    Returns:  
        tuple: Um proxy (IP, porta) se encontrado; caso contrário, None.  
    """  
    try:  
        if source == 'us_proxy':  
            url = "https://www.us-proxy.org/"  
            regex = r'<tr><td>(\d+\.\d+\.\d+\.\d+)</td><td>(\d+)</td><td>.*?</td><td>.*?</td><td>.*?</td><td class="hx">yes</td>' 
        elif source == 'free_proxy_list':  
            url = "https://free-proxy-list.net/"  
            regex = r'<tr><td>(\d+\.\d+\.\d+\.\d+)</td><td>(\d+)</td>'  
        elif source == 'ssl_proxies':  
            url = "https://www.sslproxies.org/"  
            regex = r'<tr><td>(\d+\.\d+\.\d+\.\d+)</td><td>(\d+)</td>'  
          
        response = requests.get(url)  
        matches = re.findall(regex, response.text)  
        proxy_list = [(ip, port) for ip, port in matches]  
        return random.choice(proxy_list) if proxy_list else None  
    except Exception as e:  
        logger.error(f"Erro ao obter proxies da fonte {source}: {e}")  
        return None  


def check_proxy(proxy):  
    """  
    Verifica se um proxy está funcionando.  
  
    Args:  
        proxy (tuple): O proxy (IP, porta) a ser verificado.  
  
    Returns:  
        bool: True se o proxy estiver funcionando; caso contrário, False.  
    """  
    proxies = {  
        "http": f"http://{proxy[0]}:{proxy[1]}",  
        "https": f"http://{proxy[0]}:{proxy[1]}"  
    }  
  
    try:  
        response = requests.get("https://httpbin.io/ip", proxies=proxies, timeout=1)  
        if response.status_code == 200:  
            return True  
        else:  
            logger.warning(f"Proxy retornou status code {response.status_code}")  
    except Exception as e:  
        logger.error(f"Erro ao conectar com o proxy: {e}")  
    return False  


def get_working_proxy(attempts_per_provider=50):  
    """  
    Tenta obter um proxy funcional.  
  
    Args:  
        attempts_per_provider(int): Número de tentativas por provedor antes de passar para o próximo.  
  
    Returns:  
        tuple: Um proxy funcional (IP, porta); caso contrário, None.  
    """  
    sources = ['us_proxy', 'free_proxy_list', 'ssl_proxies']  
      
    for source in sources:  
        logger.info(f"Tentando obter um proxy da fonte: {source}")  
        for _ in range(attempts_per_provider):  
            proxy = get_free_proxy(source)  
            if proxy and check_proxy(proxy):  
                return proxy  
    return None  

def get_driver(site_url: str, headless: bool = False, use_proxy: bool = False) -> Selenium:  
    """  
    Inicializa o driver Selenium com suporte a proxies rotativos usando RPA Framework.  
  
    Args:  
        site_url (str): URL do site que será acessado pelo navegador.  
        headless (bool): Define se o navegador deve rodar em modo headless. Default é False.  
  
    Returns:  
        Selenium: Instância do navegador configurada pelo RPA Framework.  
    """  
    try:  
        browser = Selenium()  
        logger.info("Criando objeto navegador")  

        options = Options()
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--window-size=1920,1080")
        # Exclude the collection of enable-automation switches
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation"]
        )
        # Turn-off userAutomationExtension
        options.add_experimental_option("useAutomationExtension", False)
        
        if use_proxy: 
        # Obtém um proxy gratuito e verifica se está funcionando.  
            proxy = get_working_proxy()  
            if proxy:  
                options.append(f"--proxy-server=http://{proxy[0]}:{proxy[1]}")  
                logger.info(f"Usando Proxy {proxy[0]}:{proxy[1]}")  
            else:  
                logger.warning("Nenhum proxy funcional encontrado. Continuando sem proxy.")  
          
        if headless:  
            options.append("--headless")  
            options.append("--window-size=1920x1080")  
         
        
        browser.open_available_browser("about:blank", options=options)  
        browser.maximize_browser_window()  
        browser.set_selenium_page_load_timeout(60)  
          
        # Verifica o IP atual  
        browser.go_to("https://httpbin.io/ip")  
        ip_info = browser.get_text("css=body")  
        logger.info(f"IP Atual: {ip_info}")  
          
        # Acessa o site desejado  
        logger.info(f"Acessando o site: {site_url}")  
        browser.go_to(url=site_url)  
        
        browser.delete_all_cookies()
        # driver.set_window_size(1920, 1080)
        browser.driver.execute_script(
        'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        )

        browser.execute_cdp(
        "Network.setUserAgentOverride",
        {
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/117.0.0.0 Safari/537.36"
        },
        )
        logger.info(browser.execute_javascript("return navigator.userAgent;"))
          
        return browser  
    except Exception as e:  
        logger.error(f"Erro encontrado na rotina get_browser: {traceback.format_exc()}")  
        return None  

def normalize(t: str) -> str:
    return t.lower().strip()

def random_delay(min_delay=1, max_delay=5):
    time.sleep(random.uniform(min_delay, max_delay))

def center_element(driver, elm):
    """
    Centers an element on the page.
    """
    # Will this ever work? It seems like if the element is off the page, by definition it's
    # not clickable
    # wait = WebDriverWait(driver, 5)
    # and wait.until(EC.element_to_be_clickable(elm))
    if elm:
        driver.execute_script(
            "arguments[0].scrollIntoView({'block':'center','inline':'center'})", elm
        )
    return elm


def slow_send_keys(el, text, unfocus_on_complete=True):
    """
    Sends keys to an element slowly, one character at a time. There will be a random delay between
    each character.
    This is useful to avoid bot detection when inserting a text in a field.
    :param el: Selenium element
    :param text: text to insert
    """
    if el:
        el.click()

        # some fields need validation, wait before inserting text
        sleep(0.5)
        try:
            el.clear()
        except:
            pass
        for c in text:
            el.send_keys(c)
            sleep(0.01 * random.uniform(0.9, 1.2))

        if unfocus_on_complete:
            # once the value is set. it need to be validated again. that means switching to a different
            # field to trigger any js checks
            el.send_keys(Keys.TAB)


def js_click(driver, elm):
    """
    Clicks an element with javascript. This is useful for elements that are not clickable or
    displayed.
    :param driver: chrome driver
    :param elm: Selenium element
    :return: the element
    """
    try:
        if elm:
            driver.execute_script("arguments[0].click();", elm)
        return elm
    except (
        ElementClickInterceptedException,
        ElementNotInteractableException,
        JavascriptException,
        NoSuchElementException,
        TimeoutException
    ) as e:
        logger.critical(f"Exception occurred: {str(e)}")
        return None

def click_elm(driver, elm, timeout=Timeout):
    try:
        label = "Trying to click"

        def get():
            return [
                 WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable(elm)
                )
            ]
        element_to_click =  find_it(driver, elements=get, timeout=timeout, label=label)
        if element_to_click:

            return element_to_click.click()
        else:
            return None
    except (
        ElementClickInterceptedException,
        ElementNotInteractableException,
        JavascriptException,
        NoSuchElementException,
        TimeoutException
    ) as e:
        logger.critical(f"Exception occurred: {str(e)}")
        return None

def find_with_label(driver, tag, label, timeout=Timeout):
    try:
        return find_with_attribute(driver, tag, "aria-label", label, timeout)
    except (
        ElementClickInterceptedException,
        ElementNotInteractableException,
        JavascriptException,
        NoSuchElementException,
        TimeoutException
    ) as e:
        logger.critical(f"Exception occurred: {str(e)}")
        return None


def find_all_with_attribute(driver, tag, attr, value, timeout=Timeout):
    try:
        target = normalize(value)
        return [
            e
            for e in WebDriverWait(driver, timeout).until(
                EC.visibility_of_any_elements_located(locator=[By.TAG_NAME, tag])
            )
            if e.get_attribute(attr) and (target in normalize(e.get_attribute(attr)))
        ]
    except (
        ElementClickInterceptedException,
        ElementNotInteractableException,
        JavascriptException,
        NoSuchElementException,
        TimeoutException
    ) as e:
        logger.critical(f"Exception occurred: {str(e)}")
        return None


def find_all_elm_with_attribute(elm: WebElement, tag, attr, value, timeout=Timeout):
    try:
        target = normalize(value)
        return [
            e
            for e in elm.find_elements(By.TAG_NAME, tag)
            if e.get_attribute(attr) and (target in normalize(e.get_attribute(attr)))
        ]
    except (
        ElementClickInterceptedException,
        ElementNotInteractableException,
        JavascriptException,
        NoSuchElementException,
        TimeoutException
    ) as e:
        logger.critical(f"Exception occurred: {str(e)}")
        return None


def find_elm_with_attribute(
    elm: WebElement, tag_attr_value: TagAttVl | list[TagAttVl], timeout=Timeout
) -> WebElement | None:
    if not isinstance(tag_attr_value, list):
        tag_attr_value = [tag_attr_value]
    for selector in tag_attr_value:
        try:
            target = normalize(selector.vlr)
            logger.debug(
                f"Trying to find:{selector.attr}  - with: {selector.tag} and: {target}"
            )
            sleep(0.2)
            e = elm.find_element(By.TAG_NAME, selector.tag)
            if e.get_attribute(selector.attr) and (
                target in normalize(e.get_attribute(selector.attr))
            ):
                logger.debug(
                    f"Found: {selector.attr} - with: {selector.tag} and: {target}"
                )
                sleep(0.4)
                return e
        except (NoSuchElementException, TimeoutException):
            logger.debug(
                f"Not Found: {selector.attr} - with: {selector.tag} and: {target}"
            )
            continue


def find_elm_picture(elm: WebElement, selector: Selector, timeout=Timeout):
    try:
        logger.debug(f"Trying to find:{selector.css}")
        sleep(0.2)
        e = WebDriverWait(elm, timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, selector.css))
        )
        if e:
            str_picture = e.get_attribute("src")
            sleep(0.4)
            return str_picture
    except (NoSuchElementException, TimeoutException):
        logger.debug(f"Not Found: {selector.css}")


def find_with_attribute(driver, tag, attr, value, timeout=Timeout):
    try:
        label = "find_with_attribute %s %s %s" % (tag, attr, value)
        return find_it(
            driver,
            lambda: find_all_with_attribute(driver, tag, attr, value),
            timeout=timeout,
            label=label,
        )
    except (
        ElementClickInterceptedException,
        ElementNotInteractableException,
        JavascriptException,
        NoSuchElementException,
        TimeoutException
    ) as e:
        logger.critical(f"Exception occurred: {str(e)}")
        return None


def find_with_text(driver, tag, text, timeout=Timeout):
    try:
        target = normalize(text)
        label = "find_with_text %s %s" % (tag, target)

        def get():
            return [
                e
                for e in WebDriverWait(driver, timeout).until(
                    EC.visibility_of_any_elements_located(locator=[By.TAG_NAME, tag])
                )
                if target in normalize(e.text)
            ]

        return find_it(driver, get, timeout=timeout, label=label)
    except (
        ElementClickInterceptedException,
        ElementNotInteractableException,
        JavascriptException,
        NoSuchElementException,
        TimeoutException
    ) as e:
        logger.critical(f"Exception occurred: {str(e)}")
        return None


def find_css_with_text(driver, css_selector, text, timeout=Timeout):
    try:
        target = normalize(text)
        label = f"find_css_with_text {css_selector} {target}"

        def get():
            return [
                e
                for e in WebDriverWait(driver, timeout).until(
                    EC.visibility_of_any_elements_located(
                        locator=[By.CSS_SELECTOR, css_selector]
                    )
                )
                if target in normalize(e.text)
            ]

        return find_it(driver, get, timeout=timeout, label=label)
    except (
        ElementClickInterceptedException,
        ElementNotInteractableException,
        JavascriptException,
        NoSuchElementException,
        TimeoutException
    ) as e:
        logger.critical(f"Exception occurred: {str(e)}")
        return None


def find_css(driver, css_selector, timeout=Timeout):
    try:
        label = "find_css %s" % css_selector

        def get():
            return [
                e
                for e in WebDriverWait(driver, timeout).until(
                    EC.visibility_of_any_elements_located(
                        locator=[By.CSS_SELECTOR, css_selector]
                    )
                )
            ]

        return find_it(driver, elements=get, timeout=timeout, label=label)
    except (
        ElementClickInterceptedException,
        ElementNotInteractableException,
        JavascriptException,
        NoSuchElementException,
        TimeoutException
    ) as e:
        logger.critical(f"Exception occurred: {str(e)}")
        return None


def find_all_css(driver: WebDriver, css_selector, timeout=Timeout):
    try:
        return driver.find_elements(By.CSS_SELECTOR, css_selector)
    except (
        ElementClickInterceptedException,
        ElementNotInteractableException,
        JavascriptException,
        NoSuchElementException,
        TimeoutException
    ) as e:
        logger.critical(f"Exception occurred: {str(e)}")
        return None


def find_element(
    driver: WebDriver, selectors: Selector | list[Selector], timeout: int = Timeout
) -> WebElement | None:
    """
    Find an element by css, text or xpath. If a list of selectors is provided, it will try to find the
    first one that matches.

    :param driver: chrome driver
    :param selectors: list of Selectors
    :param timeout: timeout in seconds
    :return: the element if found, None otherwise
    """
    if not isinstance(selectors, list):
        selectors = [selectors]

    for selector in selectors:
        elm = None
        logger.debug(f"Trying to find {selector.css}")
        try:
            if selector.xpath:
                elm = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located(locator=[By.XPATH, selector.xpath])
                )
            elif selector.css and selector.attr:
                attr, value = selector.attr
                elm = find_with_attribute(driver, selector.css, attr, value, timeout)
            elif selector.css and selector.text:
                elm = find_css_with_text(
                    driver, selector.css, selector.text, timeout=timeout
                )
            elif selector.css:
                elm = find_css(driver, selector.css, timeout=timeout)
            if elm:
                logger.debug(f"Found element: {elm}")
                return elm
        except NoSuchElementException:
            continue


def find_elements(
    driver: WebDriver, selectors: Selector | list[Selector], timeout: int = Timeout
) -> WebElement | None:
    """
    Find an element by css, text or xpath. If a list of selectors is provided, it will try to find the
    first one that matches.

    :param driver: chrome driver
    :param selectors: list of Selectors
    :param timeout: timeout in seconds
    :return: the element if found, None otherwise
    """
    if not isinstance(selectors, list):
        selectors = [selectors]

    for selector in selectors:
        elm = None
        logger.debug(f"Trying to find {selector.css}")
        try:
            if selector.xpath:
                elm = WebDriverWait(driver, timeout).until(
                    EC.presence_of_all_elements_located_located(
                        locator=[By.XPATH, selector.xpath]
                    )
                )
            elif selector.css and selector.attr:
                attr, value = selector.attr
                elm = find_with_attribute(driver, selector.css, attr, value, timeout)
            elif selector.css and selector.text:
                elm = find_css_with_text(
                    driver, selector.css, selector.text, timeout=timeout
                )
            elif selector.css:
                elm = find_all_css(driver, selector.css, timeout=timeout)
            if elm:
                logger.debug(f"Found element: {elm}")
                return elm
        except (TimeoutException, NoSuchElementException):
            continue


def select_option(select, option, to_string):
    """
    Selects an option in a select element. If the option is not found, it will try to find the best
    match using fuzzy matching.

    :param select: Selenium element
    :param option: option to select
    :param to_string: function to convert an option to a string (i.e. could be based in the text
        or the value)
    """
    if not select:
        return False
    retry(select.click)
    sleep(0.5)

    possible_options = sorted(
        select.find_elements(By.TAG_NAME, "option"),
        key=lambda op: difflib.SequenceMatcher(
            None, normalize(to_string(op)), normalize(str(option))
        ).ratio(),
        reverse=True,
    )
    if possible_options:
        best = possible_options[0]
        retry(best.click)
        return True
def select_option_value(select, option):
    select_option(select, option, lambda op: op.get_attribute("value"))


def select_option_text(select, option):
    select_option(select, option, lambda op: op.text)




def select_first_option(select):
    options = [v for v in [o.get_attribute('value') for o in select.find_elements(
        By.CSS_SELECTOR, 'option')] if v.strip() != '']
    value = options[0]
    select_option_value(select, value)

def find_fuzzy(elements, to_string, target):
    return sorted(
        elements,
        key=lambda op: difflib.SequenceMatcher(
            None, normalize(to_string(op)), normalize(target)
        ).ratio(),
    )[-1]


def page_contains(driver, token, timeout=Timeout):
    haystack = (
        WebDriverWait(driver, timeout)
        .until(
            EC.visibility_of_any_elements_located(locator=[By.CSS_SELECTOR, "body"])
        )[0]
        .get_attribute("innerHTML")
    )
    return re.search(token, haystack, re.IGNORECASE) is not None


def find_it(driver, elements, timeout=Timeout, label=None):
    def get():
        results = elements()
        if len(results) > 0:
            return results[0]
        return None

    return wait_for(get, timeout=timeout, label=label)


def wait_for(fun, timeout=Timeout, label=None):
    """
    Waits for a function to return a value

    :param fun: function to be called
    :param timeout: timeout in seconds
    :param label: label to be printed in the log
    """
    t = 0
    while t < timeout:
        if label:
            logger.debug("Waiting for %s" % label)
        res = fun()
        delta = 0.25
        if res:
            logger.info("Found %s" % label)
            return res
        else:
            sleep(delta)
            t = t + delta
    return fun()


def retry(fun, on_fail=lambda: True, sleep_time=1, attempts=RetryAttempts):
    for attempt in range(0, attempts):
        try:
            if attempt > 0:
                logger.info(f"Retrying {fun.__name__}. Attempt #{attempt + 1}")
            return fun()
        except DontRetryException as e:
            raise e
        except Exception as e:
            attempt = attempt + 1
            on_fail()
            if attempt >= attempts:
                raise e
            lines = traceback.format_exception(e, limit=10)
            logger.warning(
                "Retrying fun due to %s\n%s, attempt=%s of %s"
                % (str(e), "\n".join(lines), attempt, attempts)
            )
            sleep(sleep_time)


class DontRetryException(Exception):
    pass


class KickedOutofFunnelException(DontRetryException):
    pass


class Fatal(Exception):
    def __init__(self, e, metadata={}):
        self._e = e
        self._meta = metadata

    def lines(self):
        return traceback.format_exception(self._e, limit=10)

    def metadata(self):
        base = self._meta
        base["retriable"] = not isinstance(self._e, DontRetryException)
        base["exception_name"] = self._e.__class__.__name__
        base["exception_message"] = str(self._e)
        return base
