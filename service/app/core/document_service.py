import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import tempfile
import os
import re
import json
from ..config import settings

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self):
        """Initialize document service"""
        try:
            # Try to import Docling
            from docling.document_converter import DocumentConverter
            self.converter = DocumentConverter()
            self.docling_available = True
            logger.info("Docling document service initialized successfully")
        except ImportError as e:
            logger.warning(f"Docling not available, using mock service: {e}")
            self.docling_available = False
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        Process a document and return cleaned JSON data
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing cleaned document data as JSON
        """
        try:
            logger.info(f"Processing document: {file_path}")
            
            if self.docling_available:
                # Use Docling
                result = self.converter.convert(file_path)
                
                # Extract text content
                text_content = self._extract_text_content(result.document)
                
                # Clean the text data
                cleaned_data = self._clean_text_data(text_content)
                
                # Create JSON response
                json_response = {
                    'success': True,
                    'document_info': {
                        'file_path': file_path,
                        'file_name': Path(file_path).name,
                        'file_size': os.path.getsize(file_path),
                        'pages': len(result.document.pages) if hasattr(result.document, 'pages') else 1
                    },
                    'cleaned_data': cleaned_data,
                    'metadata': {
                        'processing_engine': 'docling',
                        'version': '2.47.0'
                    }
                }
            else:
                # Mock processing for testing
                mock_text = "Mock Document Processing This is a mock document processing result."
                cleaned_data = self._clean_text_data(mock_text)
                
                json_response = {
                    'success': True,
                    'document_info': {
                        'file_path': file_path,
                        'file_name': Path(file_path).name,
                        'file_size': os.path.getsize(file_path),
                        'pages': 1
                    },
                    'cleaned_data': cleaned_data,
                    'metadata': {
                        'processing_engine': 'mock',
                        'version': 'mock'
                    }
                }
            
            return json_response
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'document_info': {'file_path': file_path}
            }
    
    def _extract_text_content(self, document) -> str:
        """Extract plain text content from Docling document"""
        try:
            # Try to get text from document
            if hasattr(document, 'text'):
                return document.text
            
            # Try to get text from markdown
            markdown = document.export_to_markdown()
            # Remove markdown formatting
            text = re.sub(r'#+\s*', '', markdown)  # Remove headers
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove bold
            text = re.sub(r'\*(.*?)\*', r'\1', text)  # Remove italic
            text = re.sub(r'`(.*?)`', r'\1', text)  # Remove code
            text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # Remove links
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text content: {e}")
            return ""
    
    def _clean_text_data(self, text: str) -> str:
        """
        Clean text data by removing extra spaces and unidentified characters
        
        Args:
            text: Raw text content from document
            
        Returns:
            Cleaned text string
        """
        if not text:
            return ""
        
        # Remove extra whitespace (multiple spaces, tabs, newlines)
        cleaned = re.sub(r'\s+', ' ', text)
        
        # Remove unidentified characters (keep only printable characters and common Unicode)
        # This keeps letters, numbers, punctuation, and common symbols
        # Fixed the regex pattern to properly escape special characters
        cleaned = re.sub(r'[^\w\s\-.,;:!?()\[\]{}"\'@#$%&*+=<>/\\|~`]', '', cleaned)
        
        # Remove extra spaces around punctuation
        cleaned = re.sub(r'\s+([.,;:!?])', r'\1', cleaned)
        cleaned = re.sub(r'([.,;:!?])\s+', r'\1 ', cleaned)
        
        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()
        
        return cleaned
    
    def extract_property_details(self, text: str) -> Dict[str, Any]:
        """
        Extract property-specific details from cleaned text
        
        Args:
            text: Cleaned text content from the document
            
        Returns:
            Dictionary with extracted property details
        """
        details = {
            'state': None,
            'district': None,
            'village_town': None,
            'tahsil_sub_district': None,
            'year_of_registration': None,
            'document_number': None,
            'seller_names': [],
            'purchaser_names': [],
            'survey_number': None,
            'plot_number': None,
            'flat_number': None,
            'property_address': None,
            'registration_date': None,
            'stamp_duty': None,
            'registration_fee': None
        }
        
        # Convert to lowercase for easier matching
        text_lower = text.lower()
        lines = text.split('\n')
        
        # Extract year of registration (look for 4-digit year)
        year_pattern = r'\b(19|20)\d{2}\b'
        years = re.findall(year_pattern, text)
        if years:
            details['year_of_registration'] = years[0]
        
        # Extract document number (common patterns in property documents)
        doc_patterns = [
            r'document\s*no[.:]?\s*(\d+)',
            r'doc\s*no[.:]?\s*(\d+)',
            r'registration\s*no[.:]?\s*(\d+)',
            r'reg\s*no[.:]?\s*(\d+)',
            r'index\s*no[.:]?\s*(\d+)',
            r'index\s*2\s*no[.:]?\s*(\d+)'
        ]
        
        for pattern in doc_patterns:
            match = re.search(pattern, text_lower)
            if match:
                details['document_number'] = match.group(1)
                break
        
        # Extract survey number
        survey_patterns = [
            r'survey\s*no[.:]?\s*(\d+)',
            r'survey\s*number[.:]?\s*(\d+)',
            r's\.?no[.:]?\s*(\d+)',
            r'survey\s*(\d+)'
        ]
        
        for pattern in survey_patterns:
            match = re.search(pattern, text_lower)
            if match:
                details['survey_number'] = match.group(1)
                break
        
        # Extract plot number
        plot_patterns = [
            r'plot\s*no[.:]?\s*(\d+)',
            r'plot\s*number[.:]?\s*(\d+)',
            r'plot[.:]?\s*(\d+)',
            r'plot\s*(\d+)'
        ]
        
        for pattern in plot_patterns:
            match = re.search(pattern, text_lower)
            if match:
                details['plot_number'] = match.group(1)
                break
        
        # Extract flat number
        flat_patterns = [
            r'flat\s*no[.:]?\s*(\d+)',
            r'flat\s*number[.:]?\s*(\d+)',
            r'flat[.:]?\s*(\d+)',
            r'flat\s*(\d+)'
        ]
        
        for pattern in flat_patterns:
            match = re.search(pattern, text_lower)
            if match:
                details['flat_number'] = match.group(1)
                break
        
        # Extract state and district (common Indian states)
        states = ['maharashtra', 'karnataka', 'tamil nadu', 'kerala', 'andhra pradesh', 
                 'telangana', 'gujarat', 'rajasthan', 'madhya pradesh', 'uttar pradesh']
        
        for state in states:
            if state in text_lower:
                details['state'] = state.title()
                break
        
        # Extract seller and purchaser names (look for common patterns)
        seller_patterns = [
            r'seller[.:]?\s*([^.\n]+)',
            r'vendor[.:]?\s*([^.\n]+)',
            r'grantor[.:]?\s*([^.\n]+)',
            r'executant[.:]?\s*([^.\n]+)'
        ]
        
        purchaser_patterns = [
            r'purchaser[.:]?\s*([^.\n]+)',
            r'buyer[.:]?\s*([^.\n]+)',
            r'grantee[.:]?\s*([^.\n]+)',
            r'attorney[.:]?\s*([^.\n]+)'
        ]
        
        for pattern in seller_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                details['seller_names'].extend([m.strip() for m in matches])
        
        for pattern in purchaser_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                details['purchaser_names'].extend([m.strip() for m in matches])
        
        # Extract registration date
        date_patterns = [
            r'registration\s*date[.:]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'date\s*of\s*registration[.:]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'registered\s*on[.:]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text_lower)
            if match:
                details['registration_date'] = match.group(1)
                break
        
        # Extract stamp duty and registration fee
        stamp_patterns = [
            r'stamp\s*duty[.:]?\s*[rs]?\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'stamp\s*duty[.:]?\s*[rs]?\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
        ]
        
        fee_patterns = [
            r'registration\s*fee[.:]?\s*[rs]?\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'reg\s*fee[.:]?\s*[rs]?\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
        ]
        
        for pattern in stamp_patterns:
            match = re.search(pattern, text_lower)
            if match:
                details['stamp_duty'] = match.group(1)
                break
        
        for pattern in fee_patterns:
            match = re.search(pattern, text_lower)
            if match:
                details['registration_fee'] = match.group(1)
                break
        
        return details

# Global instance
document_service = DocumentService()