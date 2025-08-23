# app/ocr/surya_ocr_service.py - Using correct Surya predictors

import logging
from typing import List, Dict, Any, Tuple
from PIL import Image

# Correct Surya imports based on documentation
from surya.foundation import FoundationPredictor
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor
from surya.layout import LayoutPredictor

logger = logging.getLogger(__name__)

class SuryaOCRService:
    """
    Service for OCR and layout detection using Surya predictors
    Based on official Surya documentation
    """
    
    def __init__(self):
        self.predictors_loaded = False
        self._foundation_predictor = None
        self._recognition_predictor = None
        self._detection_predictor = None
        self._layout_predictor = None
    
    def load_predictors(self):
        """Load all Surya predictors"""
        if self.predictors_loaded:
            return
        
        logger.info("Loading Surya predictors...")
        
        # Load foundation predictor first
        self._foundation_predictor = FoundationPredictor()
        
        # Load other predictors
        self._recognition_predictor = RecognitionPredictor(self._foundation_predictor)
        self._detection_predictor = DetectionPredictor()
        self._layout_predictor = LayoutPredictor()
        
        self.predictors_loaded = True
        logger.info("All Surya predictors loaded successfully")
    
    def detect_layout(self, image: Image.Image) -> List[Dict[str, Any]]:
        """
        Detect layout elements using LayoutPredictor
        
        Args:
            image: PIL Image
            
        Returns:
            List of layout elements with bounding boxes and types
        """
        self.load_predictors()
        
        # Use layout predictor
        layout_predictions = self._layout_predictor([image])
        
        layout_elements = []
        for page_prediction in layout_predictions:
            for bbox_info in page_prediction.bboxes:
                element = {
                    "type": bbox_info.label,
                    "bbox": {
                        "x1": float(bbox_info.bbox[0]),
                        "y1": float(bbox_info.bbox[1]),
                        "x2": float(bbox_info.bbox[2]),
                        "y2": float(bbox_info.bbox[3])
                    },
                    "confidence": float(getattr(bbox_info, 'confidence', 1.0)),
                    "position": getattr(bbox_info, 'position', None),
                    "top_k": getattr(bbox_info, 'top_k', {})
                }
                layout_elements.append(element)
        
        logger.info(f"Detected {len(layout_elements)} layout elements")
        return layout_elements
    
    def perform_ocr(self, image: Image.Image, languages: List[str] = ["en"]) -> Tuple[List[Dict[str, Any]], str]:
        """
        Perform OCR using RecognitionPredictor with DetectionPredictor
        
        Args:
            image: PIL Image
            languages: List of language codes (not used in current Surya version)
            
        Returns:
            Tuple of (ocr_results, full_text)
        """
        self.load_predictors()
        
        # Perform OCR using recognition predictor with detection predictor
        predictions = self._recognition_predictor([image], det_predictor=self._detection_predictor)
        
        # Process results
        processed_results = []
        full_text_lines = []
        
        for page_prediction in predictions:
            for line_idx, text_line in enumerate(page_prediction.text_lines):
                ocr_result = {
                    "text": text_line.text,
                    "confidence": float(text_line.confidence),
                    "bbox": {
                        "x1": float(text_line.bbox[0]),
                        "y1": float(text_line.bbox[1]),
                        "x2": float(text_line.bbox[2]),
                        "y2": float(text_line.bbox[3])
                    },
                    "line_number": line_idx
                }
                
                processed_results.append(ocr_result)
                if text_line.text.strip():
                    full_text_lines.append(text_line.text)
        
        full_text = "\n".join(full_text_lines)
        
        logger.info(f"OCR completed: {len(processed_results)} text lines extracted")
        return processed_results, full_text
    
    def detect_text_only(self, image: Image.Image) -> List[Dict[str, Any]]:
        """
        Detect text bounding boxes only using DetectionPredictor
        
        Args:
            image: PIL Image
            
        Returns:
            List of text detection results
        """
        self.load_predictors()
        
        # Use detection predictor only
        predictions = self._detection_predictor([image])
        
        detection_results = []
        for page_prediction in predictions:
            for bbox_info in page_prediction.bboxes:
                detection = {
                    "bbox": {
                        "x1": float(bbox_info.bbox[0]),
                        "y1": float(bbox_info.bbox[1]),
                        "x2": float(bbox_info.bbox[2]),
                        "y2": float(bbox_info.bbox[3])
                    },
                    "polygon": getattr(bbox_info, 'polygon', None),
                    "confidence": float(bbox_info.confidence)
                }
                detection_results.append(detection)
        
        logger.info(f"Detected {len(detection_results)} text regions")
        return detection_results
    
    def detect_layout_and_ocr(
        self, 
        image: Image.Image, 
        languages: List[str] = ["en"],
        include_layout: bool = True
    ) -> Dict[str, Any]:
        """
        Perform both layout detection and OCR
        
        Args:
            image: PIL Image
            languages: Languages for OCR (not used in current Surya)
            include_layout: Whether to include layout detection
            
        Returns:
            Dictionary with layout and OCR results
        """
        results = {}
        
        # Layout detection
        if include_layout:
            logger.info("Starting layout detection...")
            layout_elements = self.detect_layout(image)
            results["layout_elements"] = layout_elements
        else:
            results["layout_elements"] = []
        
        # OCR
        logger.info("Starting OCR...")
        ocr_results, full_text = self.perform_ocr(image, languages)
        results["ocr_results"] = ocr_results
        results["full_text"] = full_text
        
        # Text detection (bounding boxes only)
        logger.info("Getting text detections...")
        text_detections = self.detect_text_only(image)
        results["text_detections"] = text_detections
        
        # Calculate statistics
        results["statistics"] = self._calculate_statistics(
            results.get("layout_elements", []),
            ocr_results,
            full_text
        )
        
        logger.info("Layout detection and OCR completed successfully")
        return results
    
    def _calculate_statistics(
        self, 
        layout_elements: List[Dict[str, Any]], 
        ocr_results: List[Dict[str, Any]], 
        full_text: str
    ) -> Dict[str, Any]:
        """Calculate processing statistics"""
        stats = {
            "total_layout_elements": len(layout_elements),
            "total_text_lines": len(ocr_results),
            "character_count": len(full_text),
            "word_count": len(full_text.split()) if full_text else 0,
            "average_confidence": 0.0,
            "layout_types": {}
        }
        
        # Average confidence
        if ocr_results:
            total_confidence = sum(r["confidence"] for r in ocr_results)
            stats["average_confidence"] = total_confidence / len(ocr_results)
        
        # Layout type distribution
        for element in layout_elements:
            element_type = element["type"]
            stats["layout_types"][element_type] = stats["layout_types"].get(element_type, 0) + 1
        
        return stats
    
    def extract_text_by_layout_type(
        self, 
        image: Image.Image, 
        target_types: List[str] = ["Text", "Section-header", "Caption"],
        languages: List[str] = ["en"]
    ) -> Dict[str, List[str]]:
        """
        Extract text grouped by layout element type
        
        Args:
            image: PIL Image
            target_types: Layout types to extract (from Surya's label set)
            languages: Languages for OCR
            
        Returns:
            Dictionary mapping layout types to extracted text
        """
        # Get layout and OCR results
        results = self.detect_layout_and_ocr(image, languages, include_layout=True)
        
        layout_elements = results["layout_elements"]
        ocr_results = results["ocr_results"]
        
        # Group text by layout type
        text_by_type = {layout_type: [] for layout_type in target_types}
        
        for layout_element in layout_elements:
            if layout_element["type"] in target_types:
                layout_bbox = layout_element["bbox"]
                
                # Find OCR results that overlap with this layout element
                for ocr_result in ocr_results:
                    if self._bboxes_overlap(layout_bbox, ocr_result["bbox"]):
                        text_by_type[layout_element["type"]].append(ocr_result["text"])
        
        return text_by_type
    
    def _bboxes_overlap(self, bbox1: Dict[str, float], bbox2: Dict[str, float]) -> bool:
        """Check if two bounding boxes overlap"""
        return not (
            bbox1["x2"] < bbox2["x1"] or 
            bbox2["x2"] < bbox1["x1"] or 
            bbox1["y2"] < bbox2["y1"] or 
            bbox2["y2"] < bbox1["y1"]
        )

# Optional: Additional specialized predictors if needed
class ExtendedSuryaService(SuryaOCRService):
    """
    Extended service with table recognition and LaTeX OCR
    """
    
    def __init__(self):
        super().__init__()
        self._table_predictor = None
        self._texify_predictor = None
    
    def load_additional_predictors(self):
        """Load additional predictors for specialized tasks"""
        try:
            from surya.table_rec import TableRecPredictor
            from surya.texify import TexifyPredictor
            
            self._table_predictor = TableRecPredictor()
            self._texify_predictor = TexifyPredictor()
            
            logger.info("Additional predictors loaded successfully")
        except ImportError as e:
            logger.warning(f"Additional predictors not available: {e}")
    
    def recognize_tables(self, image: Image.Image) -> List[Dict[str, Any]]:
        """
        Recognize tables in the image
        
        Args:
            image: PIL Image
            
        Returns:
            List of table recognition results
        """
        if not self._table_predictor:
            self.load_additional_predictors()
        
        if self._table_predictor:
            table_predictions = self._table_predictor([image])
            return table_predictions
        else:
            logger.warning("Table predictor not available")
            return []
    
    def extract_latex(self, image: Image.Image) -> List[Dict[str, Any]]:
        """
        Extract LaTeX from equation images
        
        Args:
            image: PIL Image (should be cropped to equation)
            
        Returns:
            List of LaTeX extraction results
        """
        if not self._texify_predictor:
            self.load_additional_predictors()
        
        if self._texify_predictor:
            latex_results = self._texify_predictor([image])
            return latex_results
        else:
            logger.warning("LaTeX predictor not available")
            return []
