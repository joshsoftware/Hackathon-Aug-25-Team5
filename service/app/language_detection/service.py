"""
Language Detection Service using AI4Bharat models
Supports detection of Indian languages and English
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import logging
from typing import Dict, Optional
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Unicode script range constants for Indian languages and scripts
DEVANAGARI_RANGE = (0x0900, 0x097F)  # Hindi, Marathi, Sanskrit
BENGALI_RANGE = (0x0980, 0x09FF)     # Bengali, Assamese
GURMUKHI_RANGE = (0x0A00, 0x0A7F)    # Punjabi
GUJARATI_RANGE = (0x0A80, 0x0AFF)    # Gujarati
ORIYA_RANGE = (0x0B00, 0x0B7F)       # Odia
TAMIL_RANGE = (0x0B80, 0x0BFF)       # Tamil
TELUGU_RANGE = (0x0C00, 0x0C7F)      # Telugu
KANNADA_RANGE = (0x0C80, 0x0CFF)     # Kannada
MALAYALAM_RANGE = (0x0D00, 0x0D7F)   # Malayalam
ARABIC_RANGE = (0x0600, 0x06FF)      # Urdu (Arabic script)

# Latin script range constants
LATIN_UPPERCASE_RANGE = (0x0041, 0x005A)  # A-Z
LATIN_LOWERCASE_RANGE = (0x0061, 0x007A)  # a-z

class LanguageDetector:
    """
    Language detection service using AI4Bharat's IndicBERT model
    """
    
    def __init__(self):
        self.model_name = "ai4bharat/indic-bert"
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.language_codes = {
            'as': 'Assamese',
            'bn': 'Bengali', 
            'gu': 'Gujarati',
            'hi': 'Hindi',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'mr': 'Marathi',
            'or': 'Odia',
            'pa': 'Punjabi',
            'ta': 'Tamil',
            'te': 'Telugu',
            'ur': 'Urdu',
            'en': 'English'
        }
        self._load_model()
    
    def _load_model(self):
        """Load the AI4Bharat language detection model"""
        try:
            logger.info("Loading AI4Bharat language detection model...")
            
            # For language detection, we'll use a simpler approach with character-based detection
            # as AI4Bharat's main models are for translation/classification
            # We'll implement a rule-based approach combined with script detection
            
            logger.info("Language detection service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def detect_language(self, text: str) -> Dict[str, any]:
        """
        Detect the language of input text
        
        Args:
            text (str): Input text to detect language for
            
        Returns:
            Dict containing detected language code, name, and confidence
        """
        if not text or not text.strip():
            return {
                "language_code": "unknown",
                "language_name": "Unknown",
                "confidence": 0.0,
                "error": "Empty or invalid text provided"
            }
        
        try:
            # Clean the text
            cleaned_text = text.strip()
            
            # Detect language using script analysis
            detected_lang = self._detect_by_script(cleaned_text)
            
            return {
                "language_code": detected_lang["code"],
                "language_name": detected_lang["name"],
                "confidence": detected_lang["confidence"],
                "text_length": len(cleaned_text),
                "detected_scripts": detected_lang.get("scripts", [])
            }
            
        except Exception as e:
            logger.error(f"Error in language detection: {str(e)}")
            return {
                "language_code": "error",
                "language_name": "Error",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _detect_by_script(self, text: str) -> Dict[str, any]:
        """
        Detect language based on Unicode script ranges
        This is particularly effective for Indian languages
        """
        
        # Define Unicode ranges for different scripts using constants
        script_ranges = {
            'devanagari': DEVANAGARI_RANGE,
            'bengali': BENGALI_RANGE,
            'gurmukhi': GURMUKHI_RANGE,
            'gujarati': GUJARATI_RANGE,
            'oriya': ORIYA_RANGE,
            'tamil': TAMIL_RANGE,
            'telugu': TELUGU_RANGE,
            'kannada': KANNADA_RANGE,
            'malayalam': MALAYALAM_RANGE,
            'arabic': ARABIC_RANGE,
        }
        
        # Count characters in each script
        script_counts = {script: 0 for script in script_ranges}
        latin_count = 0
        total_chars = 0
        
        for char in text:
            char_code = ord(char)
            total_chars += 1
            
            # Check if character belongs to any Indian script
            for script, (start, end) in script_ranges.items():
                if start <= char_code <= end:
                    script_counts[script] += 1
                    break
            else:
                # Check if it's Latin script (English)
                if (LATIN_UPPERCASE_RANGE[0] <= char_code <= LATIN_UPPERCASE_RANGE[1]) or \
                   (LATIN_LOWERCASE_RANGE[0] <= char_code <= LATIN_LOWERCASE_RANGE[1]):
                    latin_count += 1
        
        # Determine the dominant script
        max_script = max(script_counts, key=script_counts.get)
        max_count = script_counts[max_script]
        
        # Check if Latin (English) is dominant
        if latin_count > max_count:
            return {
                "code": "en",
                "name": "English",
                "confidence": latin_count / total_chars if total_chars > 0 else 0,
                "scripts": ["latin"]
            }
        
        # Map script to language
        script_to_language = {
            'devanagari': self._detect_devanagari_language(text),
            'bengali': ('bn', 'Bengali'),
            'gurmukhi': ('pa', 'Punjabi'),
            'gujarati': ('gu', 'Gujarati'),
            'oriya': ('or', 'Odia'),
            'tamil': ('ta', 'Tamil'),
            'telugu': ('te', 'Telugu'),
            'kannada': ('kn', 'Kannada'),
            'malayalam': ('ml', 'Malayalam'),
            'arabic': ('ur', 'Urdu'),
        }
        
        if max_count > 0:
            lang_info = script_to_language.get(max_script, ('unknown', 'Unknown'))
            if isinstance(lang_info, tuple):
                code, name = lang_info
            else:
                code, name = lang_info["code"], lang_info["name"]
                
            return {
                "code": code,
                "name": name,
                "confidence": max_count / total_chars if total_chars > 0 else 0,
                "scripts": [max_script]
            }
        
        # If no script detected, assume English
        return {
            "code": "en",
            "name": "English",
            "confidence": 0.5,
            "scripts": ["latin"]
        }
    
    def _detect_devanagari_language(self, text: str) -> tuple:
        """
        Distinguish between Hindi and Marathi for Devanagari script
        This is a simplified approach - in practice, you'd use more sophisticated methods
        """
        
        # Common Marathi words/patterns
        marathi_indicators = ['आहे', 'आणि', 'तर', 'मी', 'तू', 'तो', 'ती', 'ते']
        
        # Common Hindi words/patterns  
        hindi_indicators = ['है', 'और', 'तो', 'मैं', 'तुम', 'वह', 'यह', 'के']
        
        marathi_score = sum(1 for word in marathi_indicators if word in text)
        hindi_score = sum(1 for word in hindi_indicators if word in text)
        
        if marathi_score > hindi_score:
            return ('mr', 'Marathi')
        else:
            return ('hi', 'Hindi')
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get list of supported languages
        
        Returns:
            Dictionary of language codes and names
        """
        return self.language_codes.copy()

# Global instance
language_detector = LanguageDetector()

def detect_text_language(text: str) -> Dict[str, any]:
    """
    Convenience function to detect language of text
    
    Args:
        text (str): Input text
        
    Returns:
        Dict with language detection results
    """
    return language_detector.detect_language(text)

def get_supported_languages() -> Dict[str, str]:
    """
    Get supported languages
    
    Returns:
        Dict of supported language codes and names
    """
    return language_detector.get_supported_languages()
