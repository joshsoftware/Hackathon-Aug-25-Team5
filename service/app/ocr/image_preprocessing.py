# service/app/services/image_preprocessing.py
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import aiohttp
from io import BytesIO
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class ImagePreprocessor:
    """
    Service for downloading and preprocessing images
    """
    
    def __init__(self):
        pass
    
    async def download_image_from_url(self, file_url: str) -> bytes:
        """
        Download image from S3/Minio URL
        
        Args:
            file_url: URL to image file
            
        Returns:
            Raw image bytes
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to download image: HTTP {response.status}")
                    
                    content_type = response.headers.get('content-type', '')
                    if not content_type.startswith('image/'):
                        raise Exception(f"Invalid content type: {content_type}")
                    
                    return await response.read()
        except Exception as e:
            logger.error(f"Error downloading image from {file_url}: {str(e)}")
            raise
    
    def load_image_from_bytes(self, image_bytes: bytes) -> Image.Image:
        """
        Load PIL Image from bytes
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            PIL Image object
        """
        try:
            pil_image = Image.open(BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            return pil_image
        except Exception as e:
            logger.error(f"Error loading image from bytes: {str(e)}")
            raise
    
    def convert_to_black_white(self, image: Image.Image) -> Image.Image:
        """
        Convert image to black and white
        
        Args:
            image: PIL Image
            
        Returns:
            Grayscale PIL Image (in RGB mode)
        """
        try:
            # Convert to grayscale
            grayscale = image.convert('L')
            # Convert back to RGB for consistency
            return grayscale.convert('RGB')
        except Exception as e:
            logger.error(f"Error converting to black and white: {str(e)}")
            raise
    
    def enhance_contrast(self, image: Image.Image, factor: float = 2.0) -> Image.Image:
        """
        Enhance image contrast
        
        Args:
            image: PIL Image
            factor: Contrast enhancement factor (1.0 = no change)
            
        Returns:
            Enhanced PIL Image
        """
        try:
            enhancer = ImageEnhance.Contrast(image)
            return enhancer.enhance(factor)
        except Exception as e:
            logger.error(f"Error enhancing contrast: {str(e)}")
            raise
    
    def apply_sharpening(self, image: Image.Image) -> Image.Image:
        """
        Apply sharpening filter to image
        
        Args:
            image: PIL Image
            
        Returns:
            Sharpened PIL Image
        """
        try:
            return image.filter(ImageFilter.SHARPEN)
        except Exception as e:
            logger.error(f"Error applying sharpening: {str(e)}")
            raise
    
    def apply_denoising(self, image: Image.Image, kernel_size: int = 3) -> Image.Image:
        """
        Apply denoising using median filter
        
        Args:
            image: PIL Image
            kernel_size: Size of median filter kernel
            
        Returns:
            Denoised PIL Image
        """
        try:
            return image.filter(ImageFilter.MedianFilter(size=kernel_size))
        except Exception as e:
            logger.error(f"Error applying denoising: {str(e)}")
            raise
    
    def apply_adaptive_threshold(self, image: Image.Image) -> Image.Image:
        """
        Apply adaptive thresholding using OpenCV
        
        Args:
            image: PIL Image
            
        Returns:
            Thresholded PIL Image
        """
        try:
            # Convert to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive threshold
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Convert back to PIL
            return Image.fromarray(thresh).convert('RGB')
        except Exception as e:
            logger.error(f"Error applying adaptive threshold: {str(e)}")
            raise
    
    def apply_morphological_operations(self, image: Image.Image) -> Image.Image:
        """
        Apply morphological operations for cleanup
        
        Args:
            image: PIL Image
            
        Returns:
            Cleaned PIL Image
        """
        try:
            # Convert to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Define kernel
            kernel = np.ones((1, 1), np.uint8)
            
            # Apply morphological operations
            cleaned = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
            
            # Convert back to PIL
            return Image.fromarray(cleaned).convert('RGB')
        except Exception as e:
            logger.error(f"Error applying morphological operations: {str(e)}")
            raise
    
    def preprocess_image(
        self,
        image: Image.Image,
        convert_to_bw: bool = True,
        enhance_contrast: bool = True,
        contrast_factor: float = 2.0,
        denoise: bool = False,
        sharpen: bool = False,
        adaptive_threshold: bool = True,
        morphological_cleanup: bool = True
    ) -> Image.Image:
        """
        Apply complete preprocessing pipeline
        
        Args:
            image: Input PIL Image
            convert_to_bw: Convert to black and white
            enhance_contrast: Enhance contrast
            contrast_factor: Contrast enhancement factor
            denoise: Apply denoising
            sharpen: Apply sharpening
            adaptive_threshold: Apply adaptive thresholding
            morphological_cleanup: Apply morphological operations
            
        Returns:
            Preprocessed PIL Image
        """
        try:
            processed_image = image.copy()
            
            logger.info("Starting image preprocessing...")
            
            # Convert to black and white
            if convert_to_bw:
                logger.debug("Converting to black and white")
                processed_image = self.convert_to_black_white(processed_image)
            
            # Enhance contrast
            if enhance_contrast:
                logger.debug(f"Enhancing contrast with factor {contrast_factor}")
                processed_image = self.enhance_contrast(processed_image, contrast_factor)
            
            # Apply sharpening
            if sharpen:
                logger.debug("Applying sharpening")
                processed_image = self.apply_sharpening(processed_image)
            
            # Apply denoising
            if denoise:
                logger.debug("Applying denoising")
                processed_image = self.apply_denoising(processed_image)
            
            # Apply adaptive thresholding
            if adaptive_threshold:
                logger.debug("Applying adaptive threshold")
                processed_image = self.apply_adaptive_threshold(processed_image)
            
            # Apply morphological operations
            if morphological_cleanup:
                logger.debug("Applying morphological cleanup")
                processed_image = self.apply_morphological_operations(processed_image)
            
            logger.info("Image preprocessing completed")
            return processed_image
            
        except Exception as e:
            logger.error(f"Error in preprocessing pipeline: {str(e)}")
            raise
    
    async def download_and_preprocess(
        self,
        file_url: str,
        preprocess_options: Optional[Dict[str, Any]] = None
    ) -> Image.Image:
        """
        Download image from URL and apply preprocessing
        
        Args:
            file_url: URL to image file
            preprocess_options: Preprocessing configuration
            
        Returns:
            Preprocessed PIL Image
        """
        try:
            # Default options
            if preprocess_options is None:
                preprocess_options = {
                    "convert_to_bw": True,
                    "enhance_contrast": True,
                    "contrast_factor": 2.0
                }
            
            # Download image
            logger.info(f"Downloading image from {file_url}")
            image_bytes = await self.download_image_from_url(file_url)
            
            # Load image
            image = self.load_image_from_bytes(image_bytes)
            
            # Preprocess
            return self.preprocess_image(image, **preprocess_options)
            
        except Exception as e:
            logger.error(f"Error in download and preprocess: {str(e)}")
            raise
    
    def preprocess_from_bytes(
        self,
        image_bytes: bytes,
        preprocess_options: Optional[Dict[str, Any]] = None
    ) -> Image.Image:
        """
        Load and preprocess image from bytes
        
        Args:
            image_bytes: Raw image bytes
            preprocess_options: Preprocessing configuration
            
        Returns:
            Preprocessed PIL Image
        """
        try:
            # Default options
            if preprocess_options is None:
                preprocess_options = {
                    "convert_to_bw": True,
                    "enhance_contrast": True,
                    "contrast_factor": 2.0
                }
            
            # Load image
            image = self.load_image_from_bytes(image_bytes)
            
            # Preprocess
            return self.preprocess_image(image, **preprocess_options)
            
        except Exception as e:
            logger.error(f"Error preprocessing from bytes: {str(e)}")
            raise