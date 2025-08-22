import logging
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_maharashtra_sro_crawler():
    driver = None
    try:
        logger.info("Initializing Chrome WebDriver...")
        driver = webdriver.Chrome()
        driver.maximize_window()
        
        # Navigate to the website
        logger.info("Navigating to Maharashtra IGR service...")
        driver.get("https://freesearchigrservice.maharashtra.gov.in/")
        
        # Wait for popup and close it
        try:
            close_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[normalize-space()='Close']"))
            )
            close_button.click()
            logger.info("Closed initial popup")
        except TimeoutException:
            logger.warning("No popup found or timeout waiting for popup")
        
        # Click on Other District Search
        try:
            other_district_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@id='btnOtherdistrictSearch']"))
            )
            other_district_btn.click()
            logger.info("Clicked on Other District Search")
        except TimeoutException:
            logger.error("Could not find Other District Search button")
            raise
        
        # Test form interactions
        try:
            # Select year
            year_dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//select[@id='ddlFromYear1']"))
            )
            year_select = webdriver.support.ui.Select(year_dropdown)
            year_select.select_by_index(4)
            logger.info("Selected year")
            
            # Select district
            district_dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#ddlDistrict1"))
            )
            district_select = webdriver.support.ui.Select(district_dropdown)
            district_select.select_by_index(1)
            logger.info("Selected district")
            
            # Wait and log success
            logger.info("Successfully completed basic form interaction test")
            
        except Exception as e:
            logger.error(f"Error during form interaction: {str(e)}")
            raise
            
    except WebDriverException as e:
        logger.error(f"WebDriver error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise
    finally:
        if driver:
            logger.info("Closing WebDriver...")
            driver.quit()

if __name__ == "__main__":
    try:
        test_maharashtra_sro_crawler()
        logger.info("Test completed successfully")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
