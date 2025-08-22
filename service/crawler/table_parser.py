from bs4 import BeautifulSoup
import json
import logging

logger = logging.getLogger(__name__)

def parse_table_to_json(html_content):
    """
    Parse HTML table content into JSON format
    Args:
        html_content (str): HTML table content as string
    Returns:
        list: List of dictionaries containing parsed data
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table', {'id': 'RegistrationGrid'})
        
        if not table:
            logger.warning("Table with ID 'RegistrationGrid' not found in HTML content")
            return []
        
        # Get headers
        headers = []
        header_row = table.find('tr', {'style': lambda x: x and 'background-color:SteelBlue' in x})
        if not header_row:
            logger.warning("Header row not found in table")
            return []
            
        for th in header_row.find_all('th'):
            headers.append(th.text.strip())
        
        # Parse rows
        result = []
        data_rows = table.find_all('tr')
        
        # Skip header row and pagination row (if present)
        data_rows = [row for row in data_rows if not (
            row.get('style') and ('background-color:SteelBlue' in row.get('style') or 'background-color:#CCCCCC' in row.get('style'))
        )]
        
        for row in data_rows:
            cells = row.find_all('td')
            if not cells:
                continue  # Skip rows without cells
                
            row_data = {}
            
            # Only process cells up to the number of headers
            for i, cell in enumerate(cells):
                if i >= len(headers):
                    break  # Skip cells beyond headers
                    
                value = cell.text.strip()
                # Handle JSON-like strings in seller and purchaser names
                if headers[i] in ['Seller Name', 'Purchaser Name'] and value.startswith('{'):
                    try:
                        # Remove curly braces and split by commas
                        names = value.strip('{}').split(',')
                        value = [name.strip() for name in names if name.strip()]
                    except Exception as e:
                        logger.warning(f"Error parsing names: {str(e)}")
                
                row_data[headers[i]] = value
            
            # Only add rows with data
            if row_data:
                result.append(row_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error parsing table: {str(e)}")
        return []

def format_registration_data(html_content):
    """
    Main function to format registration data from HTML to JSON
    Args:
        html_content (str): HTML content containing the registration table
    Returns:
        str: JSON formatted string of the data
    """
    try:
        data = parse_table_to_json(html_content)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error formatting data: {str(e)}")
        return "[]"  # Return empty array as string in case of error
