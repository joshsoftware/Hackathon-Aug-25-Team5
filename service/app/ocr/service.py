# app/services/ocr_service.py

import asyncio
import logging
from typing import Dict, Any, Optional
import time

import sys
import os
from pathlib import Path

# Add the service directory to Python path
service_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(service_dir))

from app.ocr.image_preprocessing import ImagePreprocessor
from app.ocr.surya_ocr_service import SuryaOCRService

logger = logging.getLogger(__name__)

class OCRService:
    """
    OCR service that processes images from Minio URLs and returns extracted text
    """
    
    def __init__(self):
        self.preprocessor = ImagePreprocessor()
        self.ocr_service = SuryaOCRService()
    
    def get_ocr(self, file_url: str) -> Dict[str, Any]:
        """
        Process the given image file and return OCR text.
        
        :param file_url: minio url referring to the image file being processed
        :return: OCR text in json format.
        """
        try:
            return asyncio.run(self._process_image_async(file_url))
        except Exception as e:
            logger.error(f"Error processing OCR: {e}")
            return {
                "success": False,
                "error": str(e),
                "extracted_text": "",
                "metadata": {}
            }
    
    async def _process_image_async(self, file_url: str) -> Dict[str, Any]:
        """
        Async processing pipeline for image OCR
        
        :param file_url: Minio image file URL
        :return: OCR results
        """
        start_time = time.time()
        
        preprocessing_options = {
            "convert_to_bw": True,
            "enhance_contrast": True,
            "contrast_factor": 2.5,
            "denoise": True,
            "sharpen": False,
            "adaptive_threshold": True,
            "morphological_cleanup": True
        }
        
        # Step 1: Download and preprocess image
        processed_image = await self.preprocessor.download_and_preprocess(
            file_url, 
            preprocessing_options
        )
        preprocessing_time = time.time() - start_time
        
        # Step 2: Perform OCR and layout detection
        ocr_start_time = time.time()
        ocr_results = self.ocr_service.detect_layout_and_ocr(
            processed_image,
            languages=["en", "hi"],
            include_layout=True
        )
        ocr_time = time.time() - ocr_start_time
        
        # Step 3: Prepare response
        total_time = time.time() - start_time
        extracted_text = ocr_results.get('full_text', '')
        
        return {
            "success": True,
            "extracted_text": extracted_text,
            "metadata": {
                "file_url": file_url,
                "image_size": processed_image.size,
                "processing_times": {
                    "preprocessing": round(preprocessing_time, 2),
                    "ocr": round(ocr_time, 2),
                    "total": round(total_time, 2)
                },
                "ocr_statistics": ocr_results.get('statistics', {}),
                "layout_elements": ocr_results.get('layout_elements', []),
                "extraction_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }