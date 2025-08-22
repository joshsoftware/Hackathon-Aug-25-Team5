from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class DocumentProcessRequest(BaseModel):
    file_path: str

class PropertyDetails(BaseModel):
    state: Optional[str] = None
    district: Optional[str] = None
    village_town: Optional[str] = None
    tahsil_sub_district: Optional[str] = None
    year_of_registration: Optional[str] = None
    document_number: Optional[str] = None
    seller_names: List[str] = []
    purchaser_names: List[str] = []
    survey_number: Optional[str] = None
    plot_number: Optional[str] = None
    flat_number: Optional[str] = None
    property_address: Optional[str] = None
    registration_date: Optional[str] = None
    stamp_duty: Optional[str] = None
    registration_fee: Optional[str] = None

class DocumentInfo(BaseModel):
    file_path: str
    file_name: str
    file_size: int
    pages: int

class DocumentContent(BaseModel):
    text: str
    markdown: str
    html: str
    json: Dict[str, Any]

class DocumentProcessResponse(BaseModel):
    success: bool
    document_info: Optional[DocumentInfo] = None
    content: Optional[DocumentContent] = None
    property_details: Optional[PropertyDetails] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None