import time
import random
import pandas as pd
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.common.exceptions import WebDriverException, TimeoutException

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_file(file_path):
    """Read lines from a file and return as a list."""
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def create_driver(user_agent, proxy):
    """Create a Selenium WebDriver instance with given user-agent and proxy."""
    chrome_options = Options()
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    if proxy:
        chrome_options.add_argument(f'--proxy-server={proxy}')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def mimic_human_movement():
    """Simulate human-like delays."""
    time.sleep(random.uniform(0.5, 1.5))

def scrape_data(driver):
    """Scrape data from the current page."""
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        title = soup.title.string if soup.title else 'No Title'
        logging.info(f'Scraped Title: {title}')
        return {'title': title}
    except TimeoutException:
        logging.error('Timeout while waiting for page to load.')
        return None
    except Exception as e:
        logging.error(f'Error during scraping: {e}')
        return None

def main():
    target_urls = read_file('target_url.txt')  # List of URLs to scrape
    user_agents = read_file('user_agents.txt')  # List of user-agents
    proxies = read_file('proxies.txt')  # List of proxies (optional)

    scraped_data = []

    while True:
        for url in target_urls:
            try:
                logging.info(f'Visiting: {url}')
                user_agent = random.choice(user_agents)  # Randomly select a user-agent
                proxy = random.choice(proxies) if proxies else None  # Randomly select a proxy

                driver = create_driver(user_agent, proxy)
                driver.get(url)

                mimic_human_movement()  # Add delay to mimic human interaction
                data = scrape_data(driver)

                if data:
                    scraped_data.append(data)

                driver.quit()
                time.sleep(random.uniform(1, 2))  # Wait before visiting the next URL
            except WebDriverException as e:
                logging.error(f'WebDriver error: {e}. Retrying...')
                if 'driver' in locals():
                    driver.quit()
                time.sleep(1)
                continue
            except Exception as e:
                logging.error(f'Unexpected error: {e}. Moving to the next URL.')
                if 'driver' in locals():
                    driver.quit()
                continue

        # Save collected data to a CSV file
        if scraped_data:
            df = pd.DataFrame(scraped_data)
            df.to_csv('scraped_data.csv', index=False)
            logging.info('Collected data saved to scraped_data.csv')
            scraped_data.clear()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info('Script terminated by user.')
    except Exception as e:
        logging.error(f'An unexpected error occurred: {e}')
