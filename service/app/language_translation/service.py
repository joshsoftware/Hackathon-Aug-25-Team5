"""
IndicTrans2 Only - Marathi to English Translation Service
Uses only AI4Bharat IndicTrans2 model for translation
"""

import logging
from typing import Dict, Optional
import sys
import os
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.language_detection.service import detect_text_language

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IndicTransOnlyTranslator:
    """
    Translation service using only IndicTrans2 AI4Bharat model
    """
    
    def __init__(self):
        self.indictrans2_model = None
        self.indictrans2_tokenizer = None
        self._initialize_indictrans2()
        
        # Minimal fallback dictionary for exact matches only
        self.exact_matches = {
            'नमस्कार': 'Hello',
            'धन्यवाद': 'Thank you',
            'होय': 'Yes',
            'नाही': 'No',
        }
        
        logger.info("IndicTrans2-only translator initialized")
    
    def _initialize_indictrans2(self):
        """Initialize IndicTrans2 AI4Bharat model"""
        try:
            # Check device
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {device}")
            
            # Model for Indic to English translation
            model_name = "ai4bharat/indictrans2-indic-en-1B"
            
            logger.info(f"Loading IndicTrans2 model: {model_name}")
            
            # Load tokenizer
            self.indictrans2_tokenizer = AutoTokenizer.from_pretrained(
                model_name, 
                trust_remote_code=True
            )
            
            # Load model
            self.indictrans2_model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map="auto" if device == "cuda" else None
            )
            
            # Move to device if needed
            if device == "cpu" and not hasattr(self.indictrans2_model, 'device_map'):
                self.indictrans2_model = self.indictrans2_model.to(device)
            
            logger.info("IndicTrans2 model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading IndicTrans2: {str(e)}")
            self.indictrans2_model = None
            self.indictrans2_tokenizer = None
    
    def translate_to_english(self, text: str) -> Dict[str, any]:
        """
        Main translation function - detects language and translates to English
        """
        if not text or not text.strip():
            return {
                "error": "Empty text provided",
                "original_text": text,
                "translated_text": None,
                "translation_method": None
            }
        
        text = text.strip()
        
        try:
            # Step 1: Detect language
            detection_result = detect_text_language(text)
            
            if 'error' in detection_result:
                # If detection fails, assume it's Marathi if contains Devanagari
                if self._contains_devanagari(text):
                    detected_lang = "mr"
                    detected_name = "Marathi"
                    confidence = 0.8
                else:
                    return {
                        "error": f"Language detection failed: {detection_result['error']}",
                        "original_text": text,
                        "translated_text": None,
                        "translation_method": None
                    }
            else:
                detected_lang = detection_result['language_code']
                detected_name = detection_result['language_name']
                confidence = detection_result['confidence']
            
            # Step 2: Handle based on detected language
            if detected_lang == 'en':
                return {
                    "original_text": text,
                    "detected_language": {
                        "code": detected_lang,
                        "name": detected_name,
                        "confidence": confidence
                    },
                    "translated_text": text,
                    "translation_method": "no_translation_needed",
                    "message": "Text is already in English"
                }
            
            # Step 3: Translate if Marathi or contains Devanagari
            if detected_lang == 'mr' or self._contains_devanagari(text):
                
                # Check exact match first
                if text in self.exact_matches:
                    return {
                        "original_text": text,
                        "detected_language": {
                            "code": "mr",
                            "name": "Marathi",
                            "confidence": confidence
                        },
                        "translated_text": self.exact_matches[text],
                        "translation_method": "exact_match",
                        "translation_confidence": 1.0
                    }
                
                # Use IndicTrans2
                translated_text = self._translate_with_indictrans2(text)
                
                if translated_text:
                    return {
                        "original_text": text,
                        "detected_language": {
                            "code": "mr",
                            "name": "Marathi",
                            "confidence": confidence
                        },
                        "translated_text": translated_text,
                        "translation_method": "indictrans2",
                        "translation_confidence": 0.95
                    }
                else:
                    return {
                        "error": "IndicTrans2 translation failed",
                        "original_text": text,
                        "detected_language": {
                            "code": "mr",
                            "name": "Marathi",
                            "confidence": confidence
                        },
                        "translated_text": None,
                        "translation_method": None
                    }
            
            else:
                return {
                    "error": f"Unsupported language: {detected_name}. Only Marathi and English are supported.",
                    "original_text": text,
                    "detected_language": {
                        "code": detected_lang,
                        "name": detected_name,
                        "confidence": confidence
                    },
                    "translated_text": None,
                    "translation_method": None
                }
                
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return {
                "error": f"Translation failed: {str(e)}",
                "original_text": text,
                "translated_text": None,
                "translation_method": None
            }
    
    def _translate_with_indictrans2(self, text: str) -> Optional[str]:
        """
        Translate using IndicTrans2 model only
        """
        try:
            if not self.indictrans2_model or not self.indictrans2_tokenizer:
                logger.error("IndicTrans2 model not available")
                return None
            
            # Prepare input - IndicTrans2 expects source language prefix
            input_text = f"<2en> {text}"  # <2en> means "translate to English"
            
            # Tokenize
            inputs = self.indictrans2_tokenizer(
                input_text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=256
            )
            
            # Generate translation
            with torch.no_grad():
                outputs = self.indictrans2_model.generate(
                    **inputs,
                    max_length=256,
                    num_beams=5,
                    early_stopping=True,
                    do_sample=False,
                    pad_token_id=self.indictrans2_tokenizer.pad_token_id
                )
            
            # Decode output
            translated_text = self.indictrans2_tokenizer.decode(
                outputs[0], 
                skip_special_tokens=True
            )
            
            # Clean up the output
            translated_text = self._clean_translation(translated_text)
            
            if translated_text and translated_text.strip() and translated_text != text:
                logger.info(f"IndicTrans2 success: '{text}' -> '{translated_text}'")
                return translated_text
            else:
                logger.warning(f"IndicTrans2 produced empty or same result for: '{text}'")
                return None
                
        except Exception as e:
            logger.error(f"IndicTrans2 translation error: {str(e)}")
            return None
    
    def _clean_translation(self, text: str) -> str:
        """Clean and post-process translation output"""
        if not text:
            return ""
        
        # Remove common prefixes/artifacts
        prefixes_to_remove = ['<2en>', '<en>', 'en:', 'english:', 'translation:']
        text = text.strip()
        
        for prefix in prefixes_to_remove:
            if text.lower().startswith(prefix.lower()):
                text = text[len(prefix):].strip()
        
        # Basic cleanup
        text = text.strip()
        
        # Capitalize first letter if it's lowercase
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        # Fix spacing around punctuation
        replacements = {
            ' ,': ',',
            ' .': '.',
            ' !': '!',
            ' ?': '?',
            '  ': ' ',  # Remove double spaces
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def _contains_devanagari(self, text: str) -> bool:
        """Check if text contains Devanagari script (Marathi/Hindi)"""
        for char in text:
            if 0x0900 <= ord(char) <= 0x097F:  # Devanagari Unicode range
                return True
        return False
    
    def is_model_available(self) -> bool:
        """Check if IndicTrans2 model is loaded and available"""
        return self.indictrans2_model is not None and self.indictrans2_tokenizer is not None
    
    def get_model_info(self) -> Dict[str, any]:
        """Get information about the loaded model"""
        return {
            "model_available": self.is_model_available(),
            "model_name": "ai4bharat/indictrans2-indic-en-1B" if self.is_model_available() else None,
            "device": str(next(self.indictrans2_model.parameters()).device) if self.is_model_available() else None,
            "supported_languages": ["Marathi", "English"],
            "translation_direction": "Marathi -> English"
        }

# Global instance
translator = IndicTransOnlyTranslator()

def translate_text_to_english(text: str) -> Dict[str, any]:
    """
    Simple function to translate Marathi text to English using only IndicTrans2
    
    Args:
        text (str): Input text (Marathi or English)
        
    Returns:
        Dict with translation results
    """
    return translator.translate_to_english(text)

def translate_marathi_to_english(text: str) -> Optional[str]:
    """
    Direct translation function - returns only the translated text
    
    Args:
        text (str): Marathi text
        
    Returns:
        str: English translation or None if failed
    """
    if not translator.is_model_available():
        logger.error("IndicTrans2 model not available")
        return None
    
    return translator._translate_with_indictrans2(text)

def is_translator_ready() -> bool:
    """
    Check if the translator is ready to use
    
    Returns:
        bool: True if IndicTrans2 model is loaded
    """
    return translator.is_model_available()

def get_translator_info() -> Dict[str, any]:
    """
    Get information about the translator
    
    Returns:
        Dict with translator info
    """
    return translator.get_model_info()
