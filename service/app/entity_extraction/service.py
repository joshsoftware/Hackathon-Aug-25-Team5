import sys
import os
from pathlib import Path
import json
import logging
from typing import Dict, Any

# Add the service directory to Python path
current_dir = Path(__file__).parent
service_dir = current_dir.parent.parent  # Go up two levels to reach 'service'
sys.path.insert(0, str(service_dir))
logger = logging.getLogger(__name__)

from app.entity_extraction.indian_property_extraction import IndianPropertyExtraction

class EntityExtractionService:
    """
    Entity Extraction Service filtered out the required parameters from processed text
    """
    
    def __init__(self):
        self.indian_property_extraction = IndianPropertyExtraction()
    
    def get_entities(self, property_text: str) -> Dict[str, Any]:
        """
        Process the given property and return json objects of the entities.
        
        :param property_text: Property text which is processed and from SRO website and then translated to english before sending to this function
        :return: Json object of the entities.
        """
        try:
            indian_property_extraction = IndianPropertyExtraction()
            result =  indian_property_extraction.extract(property_text)
            return {
                "success": True,
                "error": "",
                "data": result,
            }
        except Exception as e:
            logger.error(f"Error processing Entity: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": {}
            }