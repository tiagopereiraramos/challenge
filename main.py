import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class Selector:
    # Helper to make it easier to pass around selectors and reduce number of args in each function
    css: str = ""
    xpath: str = ""
    text: str = ""
    attr: tuple = field(default_factory=tuple)

    def __str__(self):
        """Returns a string containing only the non-default field values."""
        s = ", ".join(
            f"{field.name}={getattr(self, field.name)!r}"
            for field in dataclasses.fields(self)
            if getattr(self, field.name)
        )
        return f"{type(self).__name__}({s})"

def find_element(driver, selector):
    return driver.find_element(By.CSS_SELECTOR, selector.css)

def simulate_human_interaction(driver):
    actions = webdriver.ActionChains(driver)
    for i in range(10):
        actions.move_by_offset(random.randint(-10, 10), random.randint(-10, 10)).perform()
        time.sleep(random.uniform(0.1, 0.3))

def center_element(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

def click_elm(driver, element):
    actions = webdriver.ActionChains(driver)
    actions.move_to_element(element).click().perform()

def slow_send_keys(el, text):
    for char in text:
        el.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))  # Espera aleatória entre as teclas

def inicial_search(driver, phrase: str):
    try:
        logger.info("Starting Scraper")
        simulate_human_interaction(driver)
        
        search_button = find_element(driver, Selector(css='button[aria-label="Open search bar"]'))
        if search_button:
            simulate_human_interaction(driver)
            center_element(driver, search_button)
            simulate_human_interaction(driver)
            click_elm(driver, search_button)
            
            search_field = find_element(driver, Selector(css="input[aria-labelledby*=react-aria]"))
            if search_field and "search" in search_field.get_attribute("type"):
                slow_send_keys(el=search_field, text=phrase)
                
                button_search = find_element(driver, Selector(css="button[aria-label='Search']"))
                if button_search:
                    simulate_human_interaction(driver)
                    click_elm(driver, button_search)
                    return True
        return False
    except Exception as e:
        logger.error(e, exc_info=True)
        return False

# Configuração do navegador
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Inicializar o driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://www.reuters.com/")

# Executar a busca inicial
inicial_search(driver, "economy")

# Finalizar o driver após a busca
time.sleep(10)
driver.quit()
