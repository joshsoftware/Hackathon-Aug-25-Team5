import logging
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from PIL import Image
import pytesseract
import time
import traceback
import os
import json
# Try both absolute and relative imports to support both direct script execution and module import
try:
    # For when running as a module (python -m crawler.service)
    from .table_parser import parse_table_to_json
except ImportError:
    # For when running directly (python crawler/service.py)
    import sys
    import os
    # Add the parent directory to sys.path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # Now we can import from crawler
    from crawler.table_parser import parse_table_to_json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CaptchaError(Exception):
    """Custom exception for CAPTCHA-related errors"""
    pass

def process_captcha_for_document_number(driver, max_retries=3):
    """
    Process CAPTCHA with validation and retry logic for document number search
    Returns True if CAPTCHA is successfully processed and validated
    """
    def enter_and_validate_captcha():
        """Helper function to enter CAPTCHA and check field validation"""
        # Take screenshot of CAPTCHA
        captcha_img = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#imgCaptcha1"))
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
        captcha_input = driver.find_element(By.XPATH, "//input[@id='TextBox1']")
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
                
                # Find and click the search button
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
                    try:
                        search_button.click()
                        logger.info("Clicked search button after initial CAPTCHA attempt")
                    except Exception as click_error:
                        logger.warning(f"Error clicking search button: {str(click_error)}")
                        try:
                            driver.execute_script("arguments[0].click();", search_button)
                            logger.info("Clicked search button with JavaScript after initial CAPTCHA attempt")
                        except Exception as js_click_error:
                            logger.warning(f"Error clicking search button with JavaScript: {str(js_click_error)}")
                
                time.sleep(2)  # Wait for page to refresh
                continue
            
            # Subsequent attempts
            if enter_and_validate_captcha():
                # Find and click the search button
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
                    try:
                        search_button.click()
                        logger.info("Clicked search button after CAPTCHA validation")
                    except Exception as click_error:
                        logger.warning(f"Error clicking search button: {str(click_error)}")
                        try:
                            driver.execute_script("arguments[0].click();", search_button)
                            logger.info("Clicked search button with JavaScript after CAPTCHA validation")
                        except Exception as js_click_error:
                            logger.warning(f"Error clicking search button with JavaScript: {str(js_click_error)}")
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
                    # If this is the second attempt, return True as we've successfully processed the CAPTCHA
                    if attempt == 1:  # Second attempt (0-indexed)
                        logger.info("Successfully processed CAPTCHA on second attempt, returning success")
                        return True
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
            
        # Wait for 20 seconds for table to appear (increased from 10 seconds)
        logger.info("Waiting for table to appear...")
        time.sleep(20)
        
        # Take a screenshot of the page for debugging
        driver.save_screenshot('page_after_search.png')
        logger.info("Saved screenshot of the page after search to page_after_search.png")
        
        # Check if the table exists
        logger.info("Checking if table exists...")
        tables = driver.find_elements(By.TAG_NAME, 'table')
        logger.info(f"Found {len(tables)} tables on the page")
        
        # Look for the specific table by ID or other attributes
        registration_table = None
        
        # First try to find by ID
        for i, table in enumerate(tables):
            try:
                table_id = table.get_attribute('id')
                logger.info(f"Table {i+1} ID: {table_id}")
                if table_id == 'RegistrationGrid':
                    registration_table = table
                    logger.info("Found RegistrationGrid table by ID")
                    break
            except Exception as e:
                logger.warning(f"Error getting table {i+1} ID: {str(e)}")
        
        # If not found by ID, try to find by structure or content
        if not registration_table:
            logger.info("RegistrationGrid table not found by ID, trying to find by structure...")
            
            # Try to find a table with registration-related headers
            for i, table in enumerate(tables):
                try:
                    # Get table headers
                    headers = table.find_elements(By.TAG_NAME, 'th')
                    header_texts = [header.text.strip() for header in headers]
                    logger.info(f"Table {i+1} headers: {header_texts}")
                    
                    # Check if this looks like a registration table
                    registration_keywords = ['DocNo', 'Document', 'Registration', 'SRO', 'Date', 'Seller', 'Purchaser']
                    matches = sum(1 for keyword in registration_keywords if any(keyword.lower() in header.lower() for header in header_texts))
                    
                    if matches >= 2:  # If at least 2 keywords match
                        registration_table = table
                        logger.info(f"Found potential registration table by headers (matched {matches} keywords)")
                        break
                except Exception as e:
                    logger.warning(f"Error checking table {i+1} headers: {str(e)}")
            
            # If still not found, try to find any table with multiple rows
            if not registration_table:
                logger.info("Registration table not found by headers, trying to find by row count...")
                for i, table in enumerate(tables):
                    try:
                        rows = table.find_elements(By.TAG_NAME, 'tr')
                        if len(rows) > 1:  # Table has more than just a header row
                            logger.info(f"Table {i+1} has {len(rows)} rows")
                            registration_table = table
                            logger.info("Found potential registration table by row count")
                            break
                    except Exception as e:
                        logger.warning(f"Error checking table {i+1} rows: {str(e)}")
        
        if not registration_table:
            logger.error("Registration table not found on the page")
            # Save page source for debugging
            with open('page_source.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            logger.info("Saved page source to page_source.html")
            
            # Take a screenshot
            driver.save_screenshot('no_table_found.png')
            logger.info("Saved screenshot to no_table_found.png")
            
            return {
                "status": "error",
                "message": "Registration table not found on the page",
                "output_file": None,
                "record_count": 0,
                "data": []
            }
        
        # Get table HTML
        table_html = registration_table.get_attribute('outerHTML')
        
        # Save the HTML for debugging
        with open('table_html.html', 'w', encoding='utf-8') as f:
            f.write(table_html)
        logger.info("Saved table HTML to table_html.html")
        
        # Parse table data
        data = parse_table_to_json(table_html)
        
        if not data:
            logger.warning("No data found in the table")
            return {
                "status": "warning",
                "message": "No data found in the table",
                "output_file": None,
                "record_count": 0,
                "data": []
            }
        
        # Save data to a JSON file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"registration_data_{timestamp}.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(data)} records to {output_file}")
        
        return {
            "status": "success",
            "message": f"Data extracted successfully",
            "output_file": output_file,
            "record_count": len(data),
            "data": data
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

def search_by_document_number(driver, doc_number="13327"):
    """
    Fill the document number search form with specific requirements:
    1. Select "Regular" radio button (which should already be checked)
    2. Select "Pune" from the district dropdown (which should already be selected)
    3. Select the 2nd option from the SRO dropdown
    4. Select "2025" from the year dropdown
    5. Enter the specified document number
    6. Click on the search button
    
    Args:
        driver: Selenium webdriver instance
        doc_number: Document number to search for (default: "13327")
    
    Returns:
        bool: True if search was successful, False otherwise
    """
    try:
        # Wait for and click Other District Search
        other_district_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='btnOtherdistrictSearch']"))
        )
        other_district_btn.click()
        logger.info("Clicked on Other District Search button")
        
        # Wait for Document Number link to be clickable
        document_number_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'दस्त निहाय/Document Number')]"))
        )
        document_number_link.click()
        logger.info("Clicked on Document Number link")
        
        # Add a longer delay after clicking Document Number to ensure the page loads
        logger.info("Waiting for page to update after Document Number selection...")
        time.sleep(5)
        
        # Take a screenshot to see what's on the page
        driver.save_screenshot('document_number_page.png')
        logger.info("Saved screenshot of the page after Document Number selection")
        
        # Log the page source to help debug
        with open('document_number_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logger.info("Saved page source after Document Number selection")
        
        # Select Regular radio button (should already be selected, but we'll ensure it)
        try:
            # Use the exact ID for the Regular radio button based on the page source
            regular_radio = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@id='rblDocType_2']"))
            )
            
            # Check if it's already selected
            if not regular_radio.is_selected():
                # Try to click with JavaScript as a fallback
                try:
                    regular_radio.click()
                    logger.info("Regular radio button clicked normally")
                except Exception as click_error:
                    logger.warning(f"Normal click failed: {str(click_error)}, trying JavaScript click")
                    driver.execute_script("arguments[0].click();", regular_radio)
                    logger.info("Regular radio button clicked with JavaScript")
            else:
                logger.info("Regular radio button already selected")
        except Exception as e:
            logger.error(f"Error selecting Regular radio button: {str(e)}")
            # Continue with the form filling even if we couldn't select the Regular radio button
        
        # Select district (Pune should already be selected, but we'll ensure it)
        try:
            district_dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#ddldistrictfordoc"))
            )
            district_select = Select(district_dropdown)
            
            # Check if Pune (value="1") is already selected
            if district_select.first_selected_option.get_attribute("value") != "1":
                district_select.select_by_value("1")  # Select Pune
                logger.info("Selected Pune district in Document Number form")
            else:
                logger.info("Pune district already selected")
            
            # Wait longer for SRO dropdown to load (increased from 3 to 10 seconds)
            logger.info("Waiting for SRO dropdown to load...")
            time.sleep(10)
        except Exception as district_error:
            logger.error(f"Error selecting district: {str(district_error)}")
        
        # Select SRO (2nd option)
        try:
            # Try multiple times to get the SRO dropdown with options
            max_retries = 3
            for retry in range(max_retries):
                try:
                    # Refresh the SRO dropdown element
                    sro_dropdown = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#ddlSROName"))
                    )
                    sro_select = Select(sro_dropdown)
                    
                    # Get all options to log them
                    options = sro_select.options
                    logger.info(f"Found {len(options)} SRO options (attempt {retry+1}/{max_retries})")
                    
                    # If we have more than just the placeholder option, break the retry loop
                    if len(options) > 1:
                        for i, option in enumerate(options):
                            logger.info(f"SRO option {i}: value={option.get_attribute('value')}, text={option.text}")
                        
                        # Always select the 1st option (index 1) as per user's instructions
                        if len(sro_select.options) > 1:
                            sro_select.select_by_index(1)  # Select the 1st option (index 1)
                            logger.info("Selected 1st SRO option (index 1) in Document Number form")
                        else:
                            logger.warning("Not enough SRO options available")
                        
                        break  # Break the retry loop
                    else:
                        # If we don't have enough options, try clicking the district dropdown again
                        logger.warning(f"Not enough SRO options on attempt {retry+1}/{max_retries}, trying to refresh...")
                        
                        # Try clicking the district dropdown again to trigger the SRO dropdown population
                        district_dropdown = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "#ddldistrictfordoc"))
                        )
                        district_select = Select(district_dropdown)
                        
                        # Re-select Pune
                        district_select.select_by_value("1")
                        logger.info("Re-selected Pune district to trigger SRO dropdown population")
                        
                        # Wait longer for SRO dropdown to load
                        time.sleep(10)
                        
                        # If this is the last retry, log a warning
                        if retry == max_retries - 1:
                            logger.warning("Failed to get SRO options after multiple attempts")
                except Exception as retry_error:
                    logger.error(f"Error on SRO retry {retry+1}/{max_retries}: {str(retry_error)}")
                    if retry == max_retries - 1:
                        raise  # Re-raise the exception on the last retry
                    time.sleep(5)  # Wait before retrying
        except Exception as sro_error:
            logger.error(f"Error selecting SRO: {str(sro_error)}")
        
        # Select year (2025)
        try:
            year_dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#ddlYearForDoc"))
            )
            year_select = Select(year_dropdown)
            
            # Check if 2025 is already selected
            if year_select.first_selected_option.get_attribute("value") != "2025":
                year_select.select_by_value("2025")  # Select 2025
                logger.info("Selected year 2025 in Document Number form")
            else:
                logger.info("Year 2025 already selected")
        except Exception as year_error:
            logger.error(f"Error selecting year: {str(year_error)}")
        
        # Enter document number
        try:
            doc_number_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#txtDocumentNo"))
            )
            doc_number_input.clear()
            doc_number_input.send_keys(doc_number)
            logger.info(f"Entered document number: {doc_number}")
        except Exception as doc_number_error:
            logger.error(f"Error entering document number: {str(doc_number_error)}")
            return False
        
        # Handle CAPTCHA for document number search
        try:
            if process_captcha_for_document_number(driver):
                logger.info("CAPTCHA processed successfully")
                
                # Wait for the table data to load (10 seconds as requested by the user)
                logger.info("Waiting 10 seconds for table data to load...")
                time.sleep(10)
                
                # Extract and convert table data to JSON
                result = extract_table_data(driver)
                
                if result["status"] == "success":
                    logger.info(f"Data extraction successful! {result['record_count']} records saved to {result['output_file']}")
                    return True
                else:
                    logger.error(f"Data extraction failed: {result['message']}")
                    return False
            else:
                logger.error("Failed to process CAPTCHA")
                return False
        except CaptchaError as e:
            logger.error(f"CAPTCHA error: {str(e)}")
            return False
        except Exception as captcha_error:
            logger.error(f"Unexpected error during CAPTCHA processing: {str(captcha_error)}")
            return False
        
    except Exception as e:
        logger.error(f"Error in search_by_document_number: {str(e)}")
        logger.error(traceback.format_exc())
        return False
