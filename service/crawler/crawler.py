import logging
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from PIL import Image
import pytesseract
import time
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CaptchaError(Exception):
    """Custom exception for CAPTCHA-related errors"""
    pass

def enter_property_number(driver, property_number='15'):
    """Helper function to enter and validate property number"""
    try:
        # Wait for property input to be clickable
        property_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='txtAttributeValue1']"))
        )
        
        # Clear any existing value
        property_input.clear()
        
        # Enter property number
        property_input.send_keys(property_number)
        
        # Verify the value was entered
        entered_value = property_input.get_attribute('value')
        if entered_value != property_number:
            logger.error(f"Property number mismatch. Expected: {property_number}, Got: {entered_value}")
            return False
            
        logger.info(f"Property number '{property_number}' entered successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error entering property number: {str(e)}")
        return False

def process_captcha(driver, max_retries=3):
    """
    Process CAPTCHA with validation and retry logic
    Returns True if CAPTCHA is successfully processed and validated
    """
    def enter_and_validate_captcha():
        """Helper function to enter CAPTCHA and check field validation"""
        # Take screenshot of CAPTCHA
        captcha_img = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#imgCaptcha_new"))
        )
        captcha_img.screenshot('captcha.png')
        
        # Process CAPTCHA image with enhanced preprocessing
        image = Image.open('captcha.png')
        
        # Convert to grayscale
        image = image.convert("L")
        
        # Increase contrast with better thresholding
        def threshold(x):
            return 255 if x > 140 else 0
        image = image.point(threshold)
        
        # Resize image to make text clearer (3x)
        width, height = image.size
        new_size = (width * 3, height * 3)
        image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Save processed image for debugging
        debug_path = f'captcha_processed_{attempt}.png'
        image.save(debug_path)
        logger.info(f"Saved processed CAPTCHA image to {debug_path}")
        
        # Try multiple OCR configurations
        configs = [
            '--psm 7 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
            '--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
            '--psm 13 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        ]
        
        for config in configs:
            captcha_text = pytesseract.image_to_string(image, config=config).strip()
            if len(captcha_text) >= 6:  # Most CAPTCHAs are 6 characters
                logger.info(f"OCR successful with config: {config}")
                break
        else:
            captcha_text = ''
        
        if not captcha_text:
            logger.warning("CAPTCHA text extraction failed")
            return False
            
        logger.info(f"CAPTCHA Text Detected: {captcha_text}")
        
        # Clear existing CAPTCHA input if any
        captcha_input = driver.find_element(By.XPATH, "//input[@id='txtImg1']")
        captcha_input.clear()
        captcha_input.send_keys(captcha_text)
        
        # Wait for field-level validation (adjust time if needed)
        time.sleep(2)
        
        # Check for field-level error with better error detection
        try:
            error_message = driver.find_element(By.ID, "lblMsg")
            if error_message.is_displayed():
                error_text = error_message.text.lower()
                if "invalid" in error_text or "incorrect" in error_text or "wrong" in error_text:
                    logger.warning(f"CAPTCHA validation failed: {error_message.text}")
                    return False
        except NoSuchElementException:
            # Also check for any other error indicators
            try:
                error_elements = driver.find_elements(By.CLASS_NAME, "error-message")
                for error in error_elements:
                    if error.is_displayed():
                        logger.warning(f"Found error message: {error.text}")
                        return False
            except:
                pass
            
            logger.info("No validation errors detected")
            return True
        
        return True

    for attempt in range(max_retries):
        try:
            logger.info(f"CAPTCHA attempt {attempt + 1} of {max_retries}")
            
            # First attempt - will likely fail but required
            if attempt == 0:
                logger.info("Performing initial CAPTCHA attempt")
                enter_and_validate_captcha()
                # Re-enter property number before clicking search
                if not enter_property_number(driver):
                    logger.error("Failed to re-enter property number")
                    continue
                search_button = driver.find_element(By.XPATH, "//input[@id='btnSearch_RestMaha']")
                search_button.click()
                time.sleep(2)  # Wait for page to refresh
                continue
            
            # Subsequent attempts
            if enter_and_validate_captcha():
                # Re-enter property number before clicking search
                if not enter_property_number(driver):
                    logger.error("Failed to re-enter property number")
                    continue
                # If field validation passes, click search
                search_button = driver.find_element(By.XPATH, "//input[@id='btnSearch_RestMaha']")
                search_button.click()
                
                # Wait for page response
                time.sleep(2)
                
                # Check for search success
                try:
                    error_message = driver.find_element(By.ID, "lblMsg")
                    if error_message.is_displayed() and "invalid" in error_message.text.lower():
                        logger.warning("Search failed after CAPTCHA")
                        continue
                except NoSuchElementException:
                    logger.info("Search successful")
                    return True
                
        except Exception as e:
            logger.error(f"Error processing CAPTCHA: {str(e)}")
            if attempt == max_retries - 1:
                raise CaptchaError(f"Failed to process CAPTCHA after {max_retries} attempts")
            
        finally:
            # Clean up CAPTCHA image file
            if os.path.exists('captcha.png'):
                os.remove('captcha.png')
    
    return False

def fill_form(driver):
    """Fill the search form with required details"""
    try:
        # Wait for and click Other District Search
        other_district_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='btnOtherdistrictSearch']"))
        )
        other_district_btn.click()
        
        # Select year
        year_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//select[@id='ddlFromYear1']"))
        )
        Select(year_dropdown).select_by_index(4)
        
        # Select district
        district_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#ddlDistrict1"))
        )
        Select(district_dropdown).select_by_index(1)
        
        # Wait for talukas to load
        time.sleep(3)  # Give time for taluka options to populate
        taluka_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//select[@id='ddltahsil']"))
        )
        Select(taluka_dropdown).select_by_index(13)
        
        # Wait for villages to load
        time.sleep(3)  # Give time for village options to populate
        village_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//select[@id='ddlvillage']"))
        )
        Select(village_dropdown).select_by_index(1)
        
        # Enter property number
        if not enter_property_number(driver):
            return False
            
        logger.info("Form filled successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error filling form: {str(e)}")
        return False

def main(debug_mode=True):
    driver = None
    try:
        # Initialize browser with longer page load timeout
        logger.info("Initializing Chrome WebDriver...")
        options = webdriver.ChromeOptions()
        options.page_load_strategy = 'normal'  # Wait for page load
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        driver.set_page_load_timeout(30)  # 30 seconds timeout
        
        # Navigate to website
        logger.info("Navigating to Maharashtra IGR service...")
        driver.get("https://freesearchigrservice.maharashtra.gov.in/")
        
        # Wait for page to be fully loaded
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Close popup if present
        try:
            close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Close']"))
            )
            close_button.click()
            logger.info("Closed initial popup")
        except TimeoutException:
            logger.warning("No popup found or timeout waiting for popup")
        
        # Fill the form
        if not fill_form(driver):
            logger.error("Failed to fill form")
            return
        
        # Process CAPTCHA with retries
        if not process_captcha(driver):
            logger.error("Failed to process CAPTCHA")
            return
            
        logger.info("Search completed successfully")
        
        if debug_mode:
            # Keep browser open in debug mode
            logger.info("Debug mode: Keeping browser open for 30 seconds...")
            time.sleep(30)
        
    except TimeoutException as e:
        logger.error(f"Page load timeout: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        if driver and not debug_mode:
            logger.info("Closing WebDriver...")
            driver.quit()

if __name__ == "__main__":
    main(debug_mode=True)  # Set to False to close browser automatically
