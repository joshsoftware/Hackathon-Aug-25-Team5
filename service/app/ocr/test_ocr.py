import sys
import os
from pathlib import Path

# Add the service directory to Python path
service_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(service_dir))

import sys
import os
from pathlib import Path

# Add the service directory to Python path
service_dir = Path(__file__).parent
sys.path.insert(0, str(service_dir))

from app.ocr.service import OCRService

def test_ocr_service():
    """Test OCR service with Minio URL"""
    
    # Initialize OCR service
    ocr_service = OCRService()
    
    # Replace with your actual Minio URL
    minio_url = "http://localhost:9000/property-docs/test-index.png"
    
    print(f"Testing OCR service with URL: {minio_url}")
    print("-" * 60)
    
    # Call OCR service
    result = ocr_service.get_ocr(minio_url)
    
    # Check results
    if result["success"]:
        print("✓ OCR processing successful!")
        print(f"✓ Extracted text length: {len(result['extracted_text'])} characters")
        print(f"✓ Processing time: {result['metadata']['processing_times']['total']}s")
        print(f"✓ Layout elements found: {len(result['metadata']['layout_elements'])}")
        print(f"✓ Image size: {result['metadata']['image_size']}")
        
        # Show text preview
        text = result["extracted_text"]
        if text:
            print(f"\nText preview (first 200 characters):")
            print(f"'{text[:200]}{'...' if len(text) > 200 else ''}'")
        else:
            print("\n⚠️ No text extracted")
        
        # Show OCR statistics
        stats = result['metadata']['ocr_statistics']
        if stats:
            print(f"\nOCR Statistics:")
            print(f"  - Text lines: {stats.get('total_text_lines', 0)}")
            print(f"  - Average confidence: {stats.get('average_confidence', 0):.3f}")
            print(f"  - Character count: {stats.get('character_count', 0)}")
            print(f"  - Word count: {stats.get('word_count', 0)}")
        
    else:
        print("❌ OCR processing failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    return result

if __name__ == "__main__":
    test_ocr_service()