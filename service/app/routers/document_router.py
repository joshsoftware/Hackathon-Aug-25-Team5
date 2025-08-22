from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Optional
import tempfile
import os
from ..core.document_service import document_service

router = APIRouter()

@router.post("/process")
async def process_document(file: UploadFile = File(...)):
    """Upload and process a document, return cleaned JSON data"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file.filename.split(".")[-1]}') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Process document
        result = document_service.process_document(temp_file_path)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract-property-details")
async def extract_property_details(file: UploadFile = File(...)):
    """Upload a document and extract only property details"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file.filename.split(".")[-1]}') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Process document
        result = document_service.process_document(temp_file_path)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        if result['success']:
            # Extract property details from cleaned data
            property_details = document_service.extract_property_details(result['cleaned_data'])
            
            return {
                'success': True,
                'property_details': property_details,
                'file_name': file.filename,
                'cleaned_data': result['cleaned_data']
            }
        else:
            return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def document_health():
    """Health check for document processing service"""
    return {"status": "healthy", "service": "document_processing"}

@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported document formats"""
    return {
        "supported_formats": [
            "PDF", "DOCX", "PPTX", "XLSX", "HTML", 
            "PNG", "TIFF", "JPEG", "WAV", "MP3"
        ],
        "processing_engine": "Docling",
        "version": "2.47.0"
    }