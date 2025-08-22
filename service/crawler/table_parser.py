import logging
import re
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_table_to_json(table_html):
    """
    Parse HTML table to JSON format
    Args:
        table_html: HTML content of the table
    Returns:
        list: List of dictionaries, each representing a row in the table
    """
    try:
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(table_html, 'html.parser')
        
        # Find all rows in the table
        rows = soup.find_all('tr')
        
        # Check if we have enough rows (at least header + one data row)
        if len(rows) < 2:
            logger.warning("Table has less than 2 rows, cannot parse")
            return []
        
        # Extract header row
        header_row = rows[0]
        headers = []
        for th in header_row.find_all('th'):
            # Clean up header text
            header_text = th.text.strip()
            headers.append(header_text)
        
        # Check if we have headers
        if not headers:
            logger.warning("No headers found in the table")
            return []
        
        logger.info(f"Found {len(headers)} headers: {headers}")
        
        # Extract data rows
        data = []
        for row in rows[1:]:
            # Skip pagination row
            if 'background-color:#CCCCCC' in str(row):
                continue
                
            # Extract cells
            cells = row.find_all(['td', 'th'])
            
            # Skip if no cells
            if not cells:
                continue
                
            # Create row data
            row_data = {}
            for i, cell in enumerate(cells):
                # Skip button cells
                if cell.find('input', {'type': 'button'}):
                    continue
                    
                # Get header for this cell
                if i < len(headers):
                    header = headers[i]
                else:
                    # If we have more cells than headers, use index as header
                    header = f"Column_{i}"
                
                # Clean up cell text
                cell_text = cell.text.strip()
                
                # Handle JSON-like content in cells
                if cell_text.startswith('{') and cell_text.endswith('}'):
                    try:
                        # Try to parse as a list of items
                        items = re.findall(r'"([^"]*)"', cell_text)
                        if items:
                            cell_text = items
                        else:
                            # Try to extract items from a different format
                            items = cell_text.strip('{}').split(',')
                            cell_text = [item.strip() for item in items if item.strip()]
                    except Exception as e:
                        logger.warning(f"Error parsing JSON-like content: {str(e)}")
                
                # Add to row data
                row_data[header] = cell_text
            
            # Add row to data if not empty
            if row_data:
                data.append(row_data)
        
        logger.info(f"Extracted {len(data)} rows of data")
        return data
        
    except Exception as e:
        logger.error(f"Error parsing table: {str(e)}")
        return []
