import logging
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from PIL import Image
import pytesseract
import time
import os
import json
import traceback
# Try both absolute and relative imports to support both direct script execution and module import
try:
    # For when running as a module (python -m crawler.service)
    from .table_parser import parse_table_to_json
    from .document_number_search import search_by_document_number
except ImportError:
    # For when running directly (python crawler/service.py)
    import sys
    import os
    # Add the parent directory to sys.path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # Now we can import from crawler
    from crawler.table_parser import parse_table_to_json
    from crawler.document_number_search import search_by_document_number

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

SRO_URL = "https://freesearchigrservice.maharashtra.gov.in/"

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
        # Try multiple selectors for property input (different forms have different IDs)
        property_input_selectors = [
            "//input[@id='txtAttributeValue1']",  # For Rest of Maharashtra form
            "//input[@id='txtAttributeValue']",   # Alternative selector
            "//input[contains(@id, 'txtAttributeValue')]",  # Partial match
            "//input[@placeholder='Enter SurveyNo./CTSNo./MilkatNo./GatNo./PlotNo.']"  # By placeholder
        ]
        
        property_input = None
        for selector in property_input_selectors:
            try:
                property_input = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                logger.info(f"Found property input with selector: {selector}")
                break
            except TimeoutException:
                logger.warning(f"Property input selector failed: {selector}")
                continue
        
        if not property_input:
            logger.error("Could not find property input field with any selector")
            return False
        
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

def process_captcha(driver, use_document_number=False, max_retries=3):
    """
    Process CAPTCHA with validation and retry logic
    Args:
        driver: Selenium webdriver instance
        use_document_number: If True, use selectors for Document Number form
        max_retries: Maximum number of retry attempts
    Returns:
        bool: True if CAPTCHA is successfully processed and validated
    """
    def enter_and_validate_captcha():
        """Helper function to enter CAPTCHA and check field validation"""
        # Take screenshot of CAPTCHA
        if use_document_number:
            # For Document Number form
            captcha_img = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#imgCaptcha1"))
            )
        else:
            # For Property Details form
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
        if use_document_number:
            # For Document Number form
            captcha_input = driver.find_element(By.XPATH, "//input[@id='TextBox1']")
        else:
            # For Property Details form
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
                # Re-enter property number before clicking search (only for Property Details form)
                if not use_document_number:
                    if not enter_property_number(driver):
                        logger.error("Failed to re-enter property number")
                        continue
                    search_button = driver.find_element(By.XPATH, "//input[@id='btnSearch_RestMaha']")
                    search_button.click()
                else:
                    # For Document Number form, find the search button
                    search_button_selectors = [
                        "//input[@type='submit' and contains(@value, 'Search')]",
                        "//input[@type='submit' and @id='btnSearch']",
                        "//input[@type='submit' and @id='btnSearchDoc']",
                        "//input[@type='submit' and not(@id='btnCancelDoc')]"  # Any submit button that's not Cancel
                    ]
                    
                    search_button = None
                    for selector in search_button_selectors:
                        try:
                            elements = driver.find_elements(By.XPATH, selector)
                            if elements:
                                search_button = elements[0]
                                break
                        except Exception as selector_error:
                            logger.warning(f"Error with selector {selector}: {str(selector_error)}")
                    
                    if search_button:
                        search_button.click()
                    else:
                        logger.error("Could not find search button for Document Number form")
                        return False
                time.sleep(2)  # Wait for page to refresh
                continue
            
            # Subsequent attempts
            if enter_and_validate_captcha():
                # Re-enter property number before clicking search (only for Property Details form)
                if not use_document_number:
                    if not enter_property_number(driver):
                        logger.error("Failed to re-enter property number")
                        continue
                    # If field validation passes, click search
                    search_button = driver.find_element(By.XPATH, "//input[@id='btnSearch_RestMaha']")
                    search_button.click()
                else:
                    # For Document Number form, find the search button
                    search_button_selectors = [
                        "//input[@type='submit' and contains(@value, 'Search')]",
                        "//input[@type='submit' and @id='btnSearch']",
                        "//input[@type='submit' and @id='btnSearchDoc']",
                        "//input[@type='submit' and not(@id='btnCancelDoc')]"  # Any submit button that's not Cancel
                    ]
                    
                    search_button = None
                    for selector in search_button_selectors:
                        try:
                            elements = driver.find_elements(By.XPATH, selector)
                            if elements:
                                search_button = elements[0]
                                break
                        except Exception as selector_error:
                            logger.warning(f"Error with selector {selector}: {str(selector_error)}")
                    
                    if search_button:
                        search_button.click()
                    else:
                        logger.error("Could not find search button for Document Number form")
                        return False
                
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

def fill_form(driver, use_document_number=False, doc_number="13327"):
    """
    Fill the search form with required details
    Args:
        driver: Selenium webdriver instance
        use_document_number: If True, select Document Number instead of Property Details
        doc_number: Document number to search for (default: "13327")
    """
    try:
        # Conditional selection between Property Details and Document Number
        if use_document_number:
            logger.info("Using document_number_search module for Document Number search")
            return search_by_document_number(driver, doc_number)
        else:
            logger.info("Using original Property Details search logic")
            
            # Original working property details search logic
            # Click on "Rest of Maharashtra" button (it's a button, not a link)
            rest_of_maharashtra_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@id='btnOtherdistrictSearch']"))
            )
            rest_of_maharashtra_button.click()
            logger.info("Clicked on Rest of Maharashtra button")
            
            # Wait for the form to load
            time.sleep(3)
            
            # Select year
            year_dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//select[@id='ddlFromYear1']"))
            )
            Select(year_dropdown).select_by_index(4)
            logger.info("Selected year")
            
            # Select district
            district_dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#ddlDistrict1"))
            )
            Select(district_dropdown).select_by_index(1)
            logger.info("Selected district")
            
            # Wait for talukas to load
            time.sleep(3)
            
            # Select taluka with better error handling
            taluka_dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//select[@id='ddltahsil']"))
            )
            taluka_select = Select(taluka_dropdown)
            taluka_options = taluka_select.options
            logger.info(f"Found {len(taluka_options)} taluka options")
            
            # Log available taluka options
            for i, option in enumerate(taluka_options):
                logger.info(f"Taluka option {i}: {option.text}")
            
            # Select a valid taluka option
            taluka_index = min(13, len(taluka_options) - 1)  # Use 13 if available, otherwise use the last option
            if taluka_index > 0:  # Skip the first option if there are more options (usually a placeholder)
                logger.info(f"Selecting taluka option at index {taluka_index}")
                taluka_select.select_by_index(taluka_index)
            else:
                logger.info("No valid taluka options found, using default")
            
            # Wait for villages to load
            time.sleep(3)
            
            # Select village with better error handling
            village_dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//select[@id='ddlvillage']"))
            )
            village_select = Select(village_dropdown)
            village_options = village_select.options
            
            # Log available village options
            logger.info(f"Found {len(village_options)} village options")
            for i, option in enumerate(village_options):
                logger.info(f"Village option {i}: {option.text}")
            
            # Select a valid village option
            village_index = min(1, len(village_options) - 1)  # Use 1 if available, otherwise use the last option
            if village_index > 0:  # Skip the first option if there are more options (usually a placeholder)
                logger.info(f"Selecting village option at index {village_index}")
                village_select.select_by_index(village_index)
            else:
                logger.info("No valid village options found, using default")
            
            # Wait for page to stabilize after village selection
            time.sleep(3)
            
            # Enter property number
            if not enter_property_number(driver):
                return False
            
            logger.info("Form filled successfully")
            return True
        
    except Exception as e:
        logger.error(f"Error filling form: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def extract_table_data(driver):
    """
    Extract data from the registration table after search
    Args:
        driver: Selenium webdriver instance
    Returns:
        dict: Result of data extraction with status and data
    """
    try:
        # Create data directory if it doesn't exist
        output_dir = "data"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Wait for 15 seconds for table to appear (increased from 10 to 15 seconds)
        logger.info("Waiting 15 seconds for table to appear...")
        time.sleep(15)
        
        # Take a screenshot of the page for debugging
        driver.save_screenshot('page_after_search.png')
        logger.info("Saved screenshot of the page after search to page_after_search.png")
        
        # Check if the table exists
        logger.info("Checking if table exists...")
        tables = driver.find_elements(By.TAG_NAME, 'table')
        logger.info(f"Found {len(tables)} tables on the page")
        
        # Look for the specific table
        registration_table = None
        for i, table in enumerate(tables):
            try:
                table_id = table.get_attribute('id')
                logger.info(f"Table {i+1} ID: {table_id}")
                if table_id == 'RegistrationGrid':
                    registration_table = table
                    logger.info("Found RegistrationGrid table")
                    break
            except Exception as e:
                logger.warning(f"Error getting table {i+1} ID: {str(e)}")
        
        if not registration_table:
            logger.error("RegistrationGrid table not found on the page")
            # Save page source for debugging
            with open('page_source.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            logger.info("Saved page source to page_source.html")
            return {
                "status": "error",
                "message": "RegistrationGrid table not found on the page",
                "output_file": None,
                "record_count": 0,
                "data": []
            }
        
        # Initialize all_data to store data from all pages
        all_data = []
        current_page = 1
        max_pages_processed = 0  # Track the highest page number processed
        page_set_base = 0  # Track the base of the current page set (0 for pages 1-10, 10 for pages 11-20, etc.)
        
        # Process all pages
        while True:
            logger.info(f"Processing page {current_page}")
            
            # Get table HTML for current page
            table_html = registration_table.get_attribute('outerHTML')
            
            # Save the HTML for debugging
            with open(f'table_html_page_{current_page}.html', 'w', encoding='utf-8') as f:
                f.write(table_html)
            logger.info(f"Saved table HTML for page {current_page} to table_html_page_{current_page}.html")
            
            # Parse table data for current page
            page_data = parse_table_to_json(table_html)
            
            if page_data:
                # Add data from current page to all_data
                all_data.extend(page_data)
                logger.info(f"Extracted {len(page_data)} records from page {current_page}")
                # Update max_pages_processed
                max_pages_processed = max(max_pages_processed, current_page)
            else:
                logger.warning(f"No data found on page {current_page}")
            
            # Check if there are more pages
            try:
                # Look for pagination row
                pagination_row = driver.find_element(By.CSS_SELECTOR, 'tr[style*="background-color:#CCCCCC"]')
                
                # Find all page links
                page_links = pagination_row.find_elements(By.TAG_NAME, 'a')
                
                # Log available page links
                logger.info(f"Found {len(page_links)} page links")
                page_link_texts = []
                for i, link in enumerate(page_links):
                    try:
                        link_text = link.text
                        page_link_texts.append(link_text)
                        logger.info(f"Page link {i+1} text: {link_text}")
                    except StaleElementReferenceException:
                        logger.warning(f"Page link {i+1} is stale, skipping")
                
                # Check if we're at the last page by looking at the last link
                # If the last link is a number and it's the current page, we're at the last page
                is_last_page = False
                if page_links:
                    try:
                        last_link = page_links[-1]
                        last_link_text = last_link.text
                        
                        # If the last link is a number and it's the current page, we're at the last page
                        if last_link_text.isdigit() and int(last_link_text) == current_page:
                            logger.info(f"Current page {current_page} is the last page (last link is {last_link_text})")
                            is_last_page = True
                        
                        # If the last link is not "..." and the current page is the highest number in the pagination
                        if last_link_text != "...":
                            # Find the highest page number in the pagination
                            highest_page = current_page
                            for link in page_links:
                                try:
                                    if link.text.isdigit() and int(link.text) > highest_page:
                                        highest_page = int(link.text)
                                except StaleElementReferenceException:
                                    continue
                            
                            if current_page == highest_page:
                                logger.info(f"Current page {current_page} is the last page (highest page in pagination)")
                                is_last_page = True
                    except StaleElementReferenceException:
                        logger.warning("Last link is stale, cannot determine if this is the last page")
                
                if is_last_page:
                    logger.info("Reached the last page, pagination complete")
                    break
                
                # Check if we're at a page that's a multiple of 10 (e.g., 10, 20, 30)
                if current_page % 10 == 0:
                    logger.info(f"At page {current_page}, looking for '...' link to navigate to next set")
                    
                    # Find all "..." links
                    dots_links = []
                    for link in page_links:
                        try:
                            if link.text == "...":
                                dots_links.append(link)
                        except StaleElementReferenceException:
                            continue
                    
                    # If there are multiple "..." links, we need to click the last one (right side)
                    if len(dots_links) > 0:
                        # Click the last "..." link (right side)
                        right_dots_link = dots_links[-1]  # Last "..." link
                        logger.info("Found '...' link at the right, clicking to see next set of pages")
                        
                        # Update the page set base before clicking
                        page_set_base = (current_page // 10) * 10
                        logger.info(f"Updating page set base to {page_set_base}")
                        
                        right_dots_link.click()
                        time.sleep(3)
                        
                        # After clicking "...", find the table and pagination again
                        registration_table = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, 'RegistrationGrid'))
                        )
                        
                        pagination_row = driver.find_element(By.CSS_SELECTOR, 'tr[style*="background-color:#CCCCCC"]')
                        page_links = pagination_row.find_elements(By.TAG_NAME, 'a')
                        
                        # Log the new pagination links
                        logger.info("New pagination links after clicking '...':")
                        new_page_link_texts = []
                        for i, link in enumerate(page_links):
                            try:
                                link_text = link.text
                                new_page_link_texts.append(link_text)
                                logger.info(f"New page link {i+1} text: {link_text}")
                            except StaleElementReferenceException:
                                logger.warning(f"New page link {i+1} is stale, skipping")
                        
                        # The expected next page number after clicking "..." at page 10, 20, etc.
                        expected_next_page = page_set_base + 11
                        logger.info(f"Expected next page after clicking '...' is {expected_next_page}")
                        
                        # Try to find the expected next page link
                        next_page_link = None
                        for link in page_links:
                            try:
                                if link.text.isdigit():
                                    page_num = int(link.text)
                                    # If we find the expected next page, use it
                                    if page_num == expected_next_page:
                                        next_page_link = link
                                        logger.info(f"Found link to expected next page {expected_next_page}")
                                        break
                                    # Otherwise, keep track of the first numeric link we find
                                    elif next_page_link is None:
                                        next_page_link = link
                                        logger.info(f"Found numeric link: page {link.text}")
                            except StaleElementReferenceException:
                                continue
                        
                        if next_page_link:
                            try:
                                next_page_text = next_page_link.text
                                logger.info(f"Clicking link to page {next_page_text}")
                                next_page_link.click()
                                time.sleep(3)
                                
                                # If the page number is small (like 2, 3, etc.) but we're expecting a higher number,
                                # adjust it based on the page set base
                                if next_page_text.isdigit():
                                    page_num = int(next_page_text)
                                    if page_num < 10 and page_set_base > 0:
                                        # This is likely the next set of pages (e.g., 11-20, 21-30)
                                        # Adjust the current page accordingly
                                        current_page = page_set_base + page_num
                                        logger.info(f"Adjusted page number from {page_num} to {current_page} based on page set base {page_set_base}")
                                    else:
                                        current_page = page_num
                                else:
                                    # If we can't parse the page number, just increment
                                    current_page += 1
                                
                                # Re-find the table after page change
                                registration_table = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.ID, 'RegistrationGrid'))
                                )
                                continue
                            except StaleElementReferenceException:
                                logger.warning("Next page link became stale, retrying pagination")
                                # Re-find pagination elements
                                pagination_row = driver.find_element(By.CSS_SELECTOR, 'tr[style*="background-color:#CCCCCC"]')
                                page_links = pagination_row.find_elements(By.TAG_NAME, 'a')
                        else:
                            logger.warning("Could not find any numeric page link after clicking '...'")
                            break
                    else:
                        logger.warning("No '...' link found at page multiple of 10")
                
                # Regular pagination - find the next page link
                next_page_found = False
                for link in page_links:
                    try:
                        # Check if this is a numeric link for the next page
                        if link.text.isdigit() and int(link.text) == current_page + 1:
                            logger.info(f"Found link to page {link.text}")
                            link.click()
                            next_page_found = True
                            current_page += 1
                            # Wait for table to update
                            time.sleep(3)
                            # Re-find the table after page change
                            registration_table = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.ID, 'RegistrationGrid'))
                            )
                            break
                    except StaleElementReferenceException:
                        continue
                
                # If no next page link found, check for "..." link
                if not next_page_found:
                    # Check for "..." link
                    dots_link = None
                    for link in page_links:
                        try:
                            if link.text == "...":
                                dots_link = link
                                break
                        except StaleElementReferenceException:
                            continue
                    
                    if dots_link:
                        logger.info("Found '...' link, clicking to see more pages")
                        
                        # Update the page set base before clicking
                        if current_page % 10 != 0:  # Only update if we're not at a multiple of 10
                            page_set_base = (current_page // 10) * 10
                            logger.info(f"Updating page set base to {page_set_base}")
                        
                        dots_link.click()
                        time.sleep(3)
                        
                        # After clicking "...", find the table again
                        registration_table = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, 'RegistrationGrid'))
                        )
                        
                        # Find the pagination row again
                        pagination_row = driver.find_element(By.CSS_SELECTOR, 'tr[style*="background-color:#CCCCCC"]')
                        page_links = pagination_row.find_elements(By.TAG_NAME, 'a')
                        
                        # Log the new pagination links
                        logger.info("New pagination links after clicking '...':")
                        for i, link in enumerate(page_links):
                            try:
                                logger.info(f"New page link {i+1} text: {link.text}")
                            except StaleElementReferenceException:
                                logger.warning(f"New page link {i+1} is stale, skipping")
                        
                        # Try to find the first numeric link in the new set
                        numeric_link = None
                        for link in page_links:
                            try:
                                if link.text.isdigit():
                                    numeric_link = link
                                    break
                            except StaleElementReferenceException:
                                continue
                        
                        if numeric_link:
                            try:
                                logger.info(f"Clicking first available numeric link: {numeric_link.text}")
                                numeric_link.click()
                                time.sleep(3)
                                
                                # If the page number is small (like 2, 3, etc.) but we're expecting a higher number,
                                # adjust it based on the page set base
                                if numeric_link.text.isdigit():
                                    page_num = int(numeric_link.text)
                                    if page_num < 10 and page_set_base > 0:
                                        # This is likely the next set of pages (e.g., 11-20, 21-30)
                                        # Adjust the current page accordingly
                                        current_page = page_set_base + page_num
                                        logger.info(f"Adjusted page number from {page_num} to {current_page} based on page set base {page_set_base}")
                                    else:
                                        current_page = page_num
                                else:
                                    # If we can't parse the page number, just increment
                                    current_page += 1
                                
                                # Re-find the table after page change
                                registration_table = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.ID, 'RegistrationGrid'))
                                )
                                continue
                            except StaleElementReferenceException:
                                logger.warning("Numeric link became stale, pagination may be incomplete")
                    
                    # If no "..." link or no numeric link found after clicking "...", we're done
                    if not dots_link or not numeric_link:
                        logger.info("No more pages found, pagination complete")
                        break
                
                # If no next page found and no "..." link, we're done
                if not next_page_found and not dots_link:
                    logger.info("No more pages found, pagination complete")
                    break
                    
            except NoSuchElementException:
                logger.info("No pagination found, only one page of results")
                break
            except Exception as e:
                logger.error(f"Error during pagination: {str(e)}")
                logger.error(traceback.format_exc())
                break
        
        # Check if we found any data
        if not all_data:
            logger.warning("No data found in any page")
            return {
                "status": "warning",
                "message": "No data found in the table",
                "output_file": None,
                "record_count": 0,
                "data": []
            }
        
        # Save all data to a single JSON file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"registration_data_{timestamp}.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(all_data)} records from {max_pages_processed} pages to {output_file}")
        
        return {
            "status": "success",
            "message": f"Data extracted successfully from {max_pages_processed} pages",
            "output_file": output_file,
            "record_count": len(all_data),
            "data": all_data
        }
        
    except Exception as e:
        logger.error(f"Error extracting table data: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Save page source for debugging
        try:
            with open('error_page_source.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            logger.info("Saved error page source to error_page_source.html")
            
            # Take a screenshot
            driver.save_screenshot('error_screenshot.png')
            logger.info("Saved error screenshot to error_screenshot.png")
        except Exception as screenshot_error:
            logger.error(f"Error saving debug info: {str(screenshot_error)}")
        
        return {
            "status": "error",
            "message": f"Data extraction failed: {str(e)}",
            "output_file": None,
            "record_count": 0,
            "data": []
        }

def main(debug_mode=True, use_document_number=False, doc_number="13327"):
    driver = None
    try:
        # Initialize browser with longer page load timeout
        logger.info("Initializing Chrome WebDriver...")
        options = webdriver.ChromeOptions()
        options.page_load_strategy = 'normal'  # Wait for page load
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        driver.set_page_load_timeout(120)  # Increased to 120 seconds timeout
        
        # Navigate to website with retry logic
        max_retries = 3
        for retry in range(max_retries):
            try:
                logger.info(f"Navigating to Maharashtra IGR service (attempt {retry+1}/{max_retries})...")
                driver.get(SRO_URL)
                # If we get here, the navigation was successful
                logger.info("Successfully navigated to the website")
                break
            except TimeoutException as e:
                if retry < max_retries - 1:
                    logger.warning(f"Page load timeout on attempt {retry+1}, retrying...")
                    # Try to refresh the page
                    try:
                        driver.refresh()
                    except:
                        pass
                else:
                    # This is the last retry, re-raise the exception
                    logger.error(f"Page load timeout after {max_retries} attempts")
                    raise
        
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
        
        # Fill the form with conditional selection
        if not fill_form(driver, use_document_number, doc_number):
            logger.error("Failed to fill form")
            return
        
        # If using document number search, the CAPTCHA and table extraction are handled in the search_by_document_number function
        if use_document_number:
            logger.info("Document number search completed")
            return
        
        # Process CAPTCHA with retries (only for property details search)
        if not process_captcha(driver, use_document_number):
            logger.error("Failed to process CAPTCHA")
            return
            
        logger.info("Search completed successfully")
        
        # Extract table data after successful search
        logger.info("Extracting table data...")
        result = extract_table_data(driver)
        
        if result["status"] == "success":
            logger.info(f"Data extraction successful! {result['record_count']} records saved to {result['output_file']}")
        else:
            logger.error(f"Data extraction failed: {result['message']}")
        
        if debug_mode:
            # Keep browser open in debug mode
            logger.info("Debug mode: Keeping browser open for 30 seconds...")
            time.sleep(30)
        
    except TimeoutException as e:
        logger.error(f"Page load timeout: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
    finally:
        if driver and not debug_mode:
            logger.info("Closing WebDriver...")
            driver.quit()

if __name__ == "__main__":
    # You can set use_document_number=True to use Document Number instead of Property Details
    # Example condition: You can implement your own condition here
    use_document_number_condition = True  # Set to True to test Document Number selection
    doc_number = "13327"  # Document number to search for
    
    main(debug_mode=True, use_document_number=use_document_number_condition, doc_number=doc_number)  # Set debug_mode to False to close browser automatically
