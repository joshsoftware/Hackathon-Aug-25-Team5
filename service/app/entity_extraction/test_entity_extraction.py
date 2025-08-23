# test_entity_service.py
import sys
import os
from pathlib import Path
import json

# Add the service directory to Python path
current_dir = Path(__file__).parent
service_dir = current_dir.parent.parent  # Go up two levels to reach 'service'
sys.path.insert(0, str(service_dir))

from app.entity_extraction.service import EntityExtractionService

def test_entity_extraction():
    """Test entity extraction service and print JSON result"""
    
    # Sample English property document text
    sample_text = """
    List No. 2 149293 Sub-Registrar: Haveli 3 23-08-2025 Document No.: 14929/2025 Note: Generated Through eSearch Module. For the original report, please contact the concerned SRO office. Regn: 63m Village Name: Aundh (1) Type of Deed: Re-conveyance (2) Consideration: 0 (3) Market Value (In case of lease, the lessor/lessee should specify): 0.01 (4) Survey details, sub-division & house number (if any): Municipal Corporation Name: Pune M.N.P. Property situated at Village Mouje Aundh, Pune, CTS No. 1134, Survey No. 128, Plot No. 57, Portion Nos. 2+3+6+7. Flat No. 4, Second Floor, Salil Apartment, having an area of 855 sq. ft. / 79.46 sq. m built-up, being released from prior mortgage deed Document No. 18115/2023 with Sub-Registrar Haveli 4, dated 26/09/2023. (Survey Number: 128) (5) Area: 79.46 sq. meters (6) In case of assessment or levy, if any. (7) Executant(s): 1) Name: Sandhya Sachin Hande, Age: 46, Address: Plot No. 0, Floor No. 0, Building Name: -, Block No. -, Road No.: M.G. Road, Naupada, Thane, Maharashtra, Thane. PIN Code: 400602, PAN No.: - 2) Name: Sachin Laxman Hande, Age: 50, Address: Plot No. 0, Floor No. 0, Building Name: -, Block No. -, Road No.: M.G. Road, Naupada, Thane, Maharashtra, Thane. PIN Code: 400602, PAN No.: - (8) Claimant: The Saraswat Co-op Bank Ltd., through Authorized Signatory Mitali Dattatraya Ankola, Age: 40, Address: Plot No. 0, Floor No. 0, Building Name: -, Block No. -, Road No.: Eknath Thakur Bhavan, 953, Appasaheb Marathe Marg, Prabhadevi, Mumbai, Maharashtra, Mumbai. PIN Code: 400025, PAN No.: ASSPB3858R (9) Date of Execution of Document: 29/05/2025 (10) Date of Registration of Document: 29/05/2025 (11) Serial No., Volume & Page: 14929/2025 (12) Stamp Duty as per Market Value: 500 (13) Registration Fees as per Market Value: 100 (14) Remarks: Valuation is not required as per the document type; hence no valuation details required. Stamp duty charged under Article: (51B)
    """
    
    # Initialize service and get entities
    entity_service = EntityExtractionService()
    result = entity_service.get_entities(sample_text)
    print(result)
    
    # Print JSON output
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_entity_extraction()