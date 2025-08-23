import re
from typing import Dict, Any


class IndianPropertyExtraction:
    """
    Service to extract structured property & party details
    from registration document text.
    """

    def extract(self, text: str) -> Dict[str, Any]:
        result = {
            "property": {
                "state": "Maharashtra",   # default
                "district": "",
                "tehsil": "",
                "village": "",
                "survey_no": "",
                "plot_no": ""
            },
            "parties": {
                "sellers": [],
                "buyers": []
            },
            "sro_office": "",
            "document_no": ""
        }

        # --------------------------
        # Document No & SRO Office
        # --------------------------
        doc_match = re.search(r'Document\s*No\.?:\s*([\w/-]+)', text, re.IGNORECASE)
        if doc_match:
            result["document_no"] = doc_match.group(1).strip()

        sro_match = re.search(r'Sub-Registrar[:\s]*([^\n,]+)', text, re.IGNORECASE)
        if sro_match:
            result["sro_office"] = sro_match.group(1).strip()
            result["property"]["tehsil"] = result["sro_office"]

        # --------------------------
        # Village / District
        # --------------------------
        village_match = re.search(r'Village\s*Name:\s*([A-Za-z\s]+)', text, re.IGNORECASE)
        if village_match:
            result["property"]["village"] = village_match.group(1).strip()

        district_match = re.search(r'Property\s+situated\s+at\s+.*?,\s*([A-Za-z]+)', text, re.IGNORECASE)
        if district_match:
            result["property"]["district"] = district_match.group(1).title()

        # --------------------------
        # Survey No & Plot No (improved)
        # --------------------------
        survey_match = re.search(r'Survey\s*No\.?\s*[:\-]?\s*([\dA-Za-z/]+)', text, re.IGNORECASE)
        if survey_match:
            result["property"]["survey_no"] = survey_match.group(1).strip()

        plot_match = re.search(r'Plot\s*No\.?\s*[:\-]?\s*([\dA-Za-z/]+)', text, re.IGNORECASE)
        if plot_match:
            result["property"]["plot_no"] = plot_match.group(1).strip()

        # --------------------------
        # Sellers (Executant(s))
        # --------------------------
        executant_section = re.search(r'Executant\(s\):(.*?)(?=\(\d+\)\s*Claimant:)', text, re.IGNORECASE | re.DOTALL)
        if executant_section:
            sellers_text = executant_section.group(1)

            seller_matches = re.finditer(
                r'Name:\s*([^,]+).*?Address:\s*([^,]+(?:,[^,]+)*).*?PAN\s*No\.?:\s*([A-Z0-9-]+)',
                sellers_text, re.IGNORECASE | re.DOTALL
            )

            for m in seller_matches:
                result["parties"]["sellers"].append({
                    "name": m.group(1).strip(),
                    "address": m.group(2).strip(),
                    "pan": m.group(3).strip().upper() if m.group(3) else ""
                })

        # --------------------------
        # Buyers (Claimant)
        # --------------------------
        claimant_section = re.search(r'Claimant:(.*?)(?=\(\d+\)\s*Date)', text, re.IGNORECASE | re.DOTALL)
        if claimant_section:
            buyers_text = claimant_section.group(1)

            buyer_matches = re.finditer(
                r'(?:Name:\s*([^,]+)|The\s+([A-Za-z\s\.-]+)).*?Address:\s*([^,]+(?:,[^,]+)*).*?PAN\s*No\.?:\s*([A-Z0-9-]+)',
                buyers_text, re.IGNORECASE | re.DOTALL
            )

            for m in buyer_matches:
                name = m.group(1) or m.group(2)
                if name:
                    result["parties"]["buyers"].append({
                        "name": name.strip(),
                        "address": m.group(3).strip(),
                        "pan": m.group(4).strip().upper() if m.group(4) else ""
                    })

        return result

