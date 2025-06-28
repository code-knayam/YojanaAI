import os
import json
from typing import List, Dict
from core.utils import clean_text_field
from core.embedding_search import index_schemes

DETAILS_DIR = os.path.join(os.path.dirname(__file__), '../../data/scheme-details')
SCHEMES_JSON_PATH = os.path.join(os.path.dirname(__file__), '../../data/schemes.json')
SCHEMES_JSON_DATA = None
SCHEMES_AGE_LIMITS = None


def load_schemes_json():
    global SCHEMES_JSON_DATA
    if SCHEMES_JSON_DATA is None:
        with open(SCHEMES_JSON_PATH, encoding='utf-8') as f:
            SCHEMES_JSON_DATA = json.load(f)
    return SCHEMES_JSON_DATA

def load_schemes_age_limits():
    global SCHEMES_AGE_LIMITS
    if SCHEMES_AGE_LIMITS is None:
        SCHEMES_AGE_LIMITS = {}
        with open(SCHEMES_JSON_PATH, encoding='utf-8') as f:
            schemes = json.load(f)
            for scheme in schemes:
                fields = scheme.get('fields', {})
                slug = fields.get('slug')
                age = fields.get('age', {})
                if slug and age:
                    SCHEMES_AGE_LIMITS[slug] = {}
                    for category, limits in age.items():
                        SCHEMES_AGE_LIMITS[slug][category] = {
                            'min_age': limits.get('gte'),
                            'max_age': limits.get('lte')
                        }
    return SCHEMES_AGE_LIMITS

def get_age_by_slug(slug: str):
    age_limits = load_schemes_age_limits()
    return age_limits.get(slug)

def extract_department_info(basic):
    """Extract and join department and ministry information"""
    dept_parts = []
    
    # Handle nodalDepartmentName
    nodal_dept = basic.get("nodalDepartmentName")
    if nodal_dept:
        if isinstance(nodal_dept, str):
            dept_parts.append(nodal_dept)
        elif isinstance(nodal_dept, dict) and nodal_dept.get("label"):
            dept_parts.append(nodal_dept["label"])
    
    # Handle nodalMinistryName
    nodal_ministry = basic.get("nodalMinistryName")
    if nodal_ministry:
        if isinstance(nodal_ministry, str):
            dept_parts.append(nodal_ministry)
        elif isinstance(nodal_ministry, dict) and nodal_ministry.get("label"):
            dept_parts.append(nodal_ministry["label"])
    
    return " - ".join(dept_parts) if dept_parts else ""

def extract_scheme_fields(scheme_obj, scheme_id):
    en = scheme_obj.get('en', {})
    basic = en.get('basicDetails', {})
    content = en.get('schemeContent', {})
    applicationProcess = en.get('applicationProcess', [])
    eligibility = en.get('eligibilityCriteria', {})

    try:
        return {
            "id": scheme_id,
            
            "name": basic.get("schemeName", ""),
            
            "ageLimits": get_age_by_slug(scheme_id),

            "department": extract_department_info(basic),

            "beneficiaries": [b.get("label", "") for b in basic.get("targetBeneficiaries", [])] if basic.get("targetBeneficiaries") else "",

            "agency": basic.get("implementingAgency", ""),
            
            "tags": basic.get("tags", []),
            
            "level": basic.get("level", {}).get("label", ""),

            "category": [c.get("label", "") for c in basic.get("schemeCategory", [])] if basic.get("schemeCategory") else "",

            "state": basic.get("state", {}).get("label", "") if basic.get("state") else "",

            "description": clean_text_field(content.get("detailedDescription_md", "")),

            "benefits": clean_text_field(content.get("benefits_md", ""))  if basic.get("benefits_md") else "",

            "exclusions": clean_text_field(content.get("exclusions_md", ""))  if basic.get("exclusions_md") else "",

            "benefitType": content.get("benefitTypes", {}).get("label", "") if basic.get("benefitTypes") else "" ,

            "applicationProcess": [clean_text_field(ap.get("process_md", "")) for ap in applicationProcess],
            
            "eligibility": clean_text_field(eligibility.get("eligibilityDescription_md", "")),
            
            "links": content.get("references", [])
        }
    except Exception as e:
        print(scheme_id, e)
        return {}

def load_all_scheme_details() -> List[Dict]:
    all_schemes = []
    for fname in os.listdir(DETAILS_DIR):
        if fname.endswith('.json'):
            with open(os.path.join(DETAILS_DIR, fname), encoding='utf-8') as f:
                data = json.load(f)
                for scheme_id, scheme_obj in data.items():
                    all_schemes.append(extract_scheme_fields(scheme_obj, scheme_id))
    
    return all_schemes

async def reindex_schemes():
    schemes = load_all_scheme_details()
    print(len(schemes))
    await index_schemes(schemes, force_reindex=True)
