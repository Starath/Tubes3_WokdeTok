# src/cv_extractor.py

import re
from typing import Dict, List, Any

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    (PLACEHOLDER) Extract text content from a PDF file.
    TODO: Implement

    Args:
        pdf_path (str): Path to the PDF file to extract text from

    Returns:
        str: Extracted text content from the PDF
    """
    return ""

def extract_summary(text: str) -> str:
    """
    Extracts the applicant's summary or profile from the CV text.

    Args:
        text (str): The full CV text to extract summary from

    Returns:
        str: Extracted summary text or "Summary not found" if no summary is found
    """
    pattern = re.compile(
        r'(?:summary|profile|objective|ringkasan)\s*:?\s*\n?(.*?)(?:\n\n|\n\s*(?:skills|experience|education|keahlian|pengalaman|pendidikan))', 
        re.IGNORECASE | re.DOTALL
    )
    match = pattern.search(text)
    if match:
        return match.group(1).strip().replace('\n', ' ')
    return "Summary not found."

def extract_skills(text: str) -> List[str]:
    """
    Extracts a list of skills from the CV text.

    Args:
        text (str): The full CV text to extract skills from

    Returns:
        List[str]: List of extracted skills, empty list if no skills are found
    """
    pattern = re.compile(
        r'(?:skills|keahlian)\s*:?\s*\n?([\s\S]*?)(?:\n\n|\n\s*(?:experience|education|projects|pengalaman|pendidikan))', 
        re.IGNORECASE
    )
    match = pattern.search(text)
    if match:
        skills_text = match.group(1).strip()
        skills = re.split(r'[\n,•-]\s*', skills_text)
        return [skill.strip() for skill in skills if skill.strip()]
    return []

def extract_experience(text: str) -> List[Dict[str, str]]:
    """
    Extracts work experience (position, company, dates) from the CV text.

    Args:
        text (str): The full CV text to extract experience from

    Returns:
        List[Dict[str, str]]: List of dictionaries containing experience details,
            each with keys: 'position', 'company', 'period'
    """
    experiences: List[Dict[str, str]] = []
    pattern = re.compile(
        r'([A-Z][a-zA-Z\s,.-]+(?:developer|engineer|manager|analyst|intern|specialist|scientist))\s*(?:at|@|di)?\s*\n?([A-Z][a-zA-Z\s,.]+ Inc\.|Corp\.|Solutions|Agency|Net)\s*\n?\((.*?)\)',
        re.IGNORECASE | re.MULTILINE
    )
    matches = pattern.findall(text)
    for match in matches:
        experiences.append({
            "position": match[0].strip(),
            "company": match[1].strip(),
            "period": match[2].strip()
        })
    return experiences

def extract_education(text: str) -> List[Dict[str, str]]:
    """
    Extracts education history (degree, university, dates) from the CV text.

    Args:
        text (str): The full CV text to extract education details from

    Returns:
        List[Dict[str, str]]: List of dictionaries containing education details,
                              each with keys: 'degree', 'institution', 'period'
    """
    educations: List[Dict[str, str]] = []    # Looks for degree, major, university, and dates
    pattern = re.compile(
        r'(B\.?Sc\.?|M\.?Sc\.?|Bachelor|Master|Sarjana|Ph\.?D)\s(?:of|in)?\s(.*?)\n(.*?University|.*?Institute of Technology|.*?Institut Teknologi.*?)\s*\n?\((.*?)\)',
        re.IGNORECASE | re.MULTILINE
    )
    matches = pattern.findall(text)
    for match in matches:
        degree = f"{match[0].strip()} in {match[1].strip()}"
        educations.append({
            "degree": degree,
            "institution": match[2].strip(),
            "period": match[3].strip()
        })
    return educations

def extract_info_from_text(full_text: str) -> Dict[str, Any]:
    """
    Takes a CV text string and returns all extracted information in a dictionary format.
    The extracted information includes summary, skills, experience, and education details.

    Args:
        full_text (str): The complete CV text to extract all information from

    Returns:
        Dict[str, Any]: Dictionary containing all extracted information 
                        with keys:'summary', 'skills', 'experience', 'education'
    """
    if not full_text:
        return {
            "summary": "CV text is empty or unavailable.",
            "skills": [],
            "experience": [],
            "education": []
        }
      # Normalize text for consistency
    full_text = re.sub(r'\s*[•●]\s*', '\n- ', full_text)

    extracted_data : Dict[str, Any]= {
        "summary": extract_summary(full_text),
        "skills": extract_skills(full_text),
        "experience": extract_experience(full_text),
        "education": extract_education(full_text)
    }
    
    return extracted_data

def extract_all_info_from_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Main integration function that extracts all information from a PDF file.
    Combines PDF text extraction and information parsing.

    Args:
        pdf_path (str): Path to the PDF file to process

    Returns:
        Dict[str, Any]: Dictionary containing all extracted information
                        with keys:'summary', 'skills', 'experience', 'education'
    """
    
    return {}

