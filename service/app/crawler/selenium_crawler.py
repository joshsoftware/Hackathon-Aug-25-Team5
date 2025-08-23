from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from table_parser import format_registration_data
import time
import json
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

class RegistrationCrawler:
    def __init__(self, max_retries=3, timeout=20):
        """
        Initialize the crawler
        Args:
            max_retries (int): Maximum number of retries for failed operations
            timeout (int): Timeout in seconds for waiting operations
        """
        self.max_retries = max_retries
        self.timeout = timeout
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        
    def setup_driver(self):
        """Setup and return Chrome driver with automatic webdriver management"""
        try:
            driver = webdriver.Chrome(
                ChromeDriverManager().install(),
                options=self.chrome_options
            )
            driver.set_page_load_timeout(self.timeout)
            return driver
        except Exception as e:
            logging.error(f"Failed to setup Chrome driver: {str(e)}")
            raise
    
    def wait_for_element(self, driver, by, value, timeout=None):
        """
        Wait for element with retry mechanism
        Args:
            driver: Selenium webdriver instance
            by: Type of locator
            value: Locator value
            timeout: Custom timeout (optional)
        Returns:
            WebElement if found
        """
        timeout = timeout or self.timeout
        retries = 0
        while retries < self.max_retries:
            try:
                element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((by, value))
                )
                return element
            except TimeoutException:
                retries += 1
                if retries == self.max_retries:
                    logging.error(f"Element {value} not found after {self.max_retries} retries")
                    raise
                logging.warning(f"Retry {retries}/{self.max_retries} for element {value}")
                time.sleep(1)
    
    def click_with_retry(self, driver, element, retries=0):
        """Click element with retry mechanism for stale elements"""
        try:
            element.click()
        except StaleElementReferenceException:
            if retries < self.max_retries:
                time.sleep(1)
                self.click_with_retry(driver, element, retries + 1)
            else:
                raise
    
    def get_table_data(self, url):
        """
        Main method to fetch table data with error handling
        Args:
            url (str): URL of the website to crawl
        Returns:
            list: List of dictionaries containing table data
        """
        driver = None
        try:
            driver = self.setup_driver()
            
            # Navigate to URL
            logging.info(f"Navigating to {url}")
            driver.get(url)
            
            # Wait for and click search button
            search_button = self.wait_for_element(driver, By.ID, "btnSearch")
            self.click_with_retry(driver, search_button)
            logging.info("Clicked search button")
            
            # Wait specifically for 10 seconds as per requirement
            logging.info("Waiting 10 seconds for table to appear...")
            time.sleep(10)
            
            # Wait for table with class and other attributes matching the provided HTML
            table_locator = (By.CSS_SELECTOR, 'table.table.table-responsive[rules="all"][id="RegistrationGrid"]')
            table = self.wait_for_element(driver, *table_locator)
            
            all_data = []
            page_num = 1
            
            while True:
                logging.info(f"Processing page {page_num}")
                # Get current page data
                table_html = table.get_attribute('outerHTML')
                page_data = json.loads(format_registration_data(table_html))
                all_data.extend(page_data)
                logging.info(f"Processed {len(page_data)} records from page {page_num}")
                
                # Check for next page using the pagination pattern from the HTML
                try:
                    # Look for pagination row
                    pagination_row = driver.find_element(By.CSS_SELECTOR, 'tr[style*="background-color:#CCCCCC"]')
                    # Find next page link that's not the current page
                    next_page_links = pagination_row.find_elements(By.CSS_SELECTOR, 'a[style="color:Black;"]')
                    
                    if page_num < len(next_page_links):
                        next_page = next_page_links[page_num]  # Get next page link
                        self.click_with_retry(driver, next_page)
                        time.sleep(2)  # Wait for table to update
                        table = self.wait_for_element(driver, *table_locator)
                        page_num += 1
                    else:
                        logging.info("No more pages available")
                        break
                        
                except NoSuchElementException:
                    logging.info("Reached last page")
                    break
                except Exception as e:
                    logging.error(f"Error navigating to next page: {str(e)}")
                    break
            
            logging.info(f"Total records collected: {len(all_data)}")
            return all_data
            
        except Exception as e:
            logging.error(f"Error during crawling: {str(e)}")
            raise
        finally:
            if driver:
                driver.quit()
                logging.info("Browser closed")
    
    def save_to_json(self, data, output_file):
        """
        Save the crawled data to a JSON file
        Args:
            data: Data to save
            output_file: Path to output file
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logging.info(f"Data saved to {output_file}")
        except Exception as e:
            logging.error(f"Error saving data to file: {str(e)}")
            raise

def main():
    if len(sys.argv) != 2:
        print("Usage: python selenium_crawler.py <website_url>")
        sys.exit(1)
        
    url = sys.argv[1]
    try:
        crawler = RegistrationCrawler()
        data = crawler.get_table_data(url)
        crawler.save_to_json(data, 'registration_data.json')
        logging.info("Crawling completed successfully")
    except Exception as e:
        logging.error(f"Crawling failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
