"""
Text extraction and parsing by gemini
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import re
import PyPDF2
from docx import Document
import warnings

# Suppress warnings from PyPDF2
warnings.filterwarnings("ignore", category=UserWarning)
load_dotenv()

# Configure Gemini
try:
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    AI_AVAILABLE = True
except Exception as e:
    AI_AVAILABLE = False
    print(f"CRITICAL: Failed to configure Gemini AI. Check GEMINI_API_KEY. Error: {e}")

def _extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        return "" # fail silently
    return text

def _extract_text_from_docx(docx_path):
    """Extract text from DOCX file"""
    try:
        doc = Document(docx_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception:
        return "" # fail silently

def _parse_with_gemini(text):
    """
    Use Google Gemini AI to extract resume information, with three-model fallback.
    Order: 2.5-flash -> 2.5-pro -> pro-latest [ to remove token limit issue ]
    """
    if not AI_AVAILABLE:
        return None

    prompt = f"""
You are an expert resume parser. Analyze the following resume text and extract structured information.

Extract these fields and return ONLY a valid JSON object:
- name: Full name of the candidate
- email: Email address
- phone: Phone number (include country code if present)
- skills: All technical and professional skills as comma-separated string
- education: Degree(s) and field of study
- college: University or College name
- experience: Years of experience OR number of roles/projects
- summary: Brief 2-line professional summary

Resume Text:
{text}

Return ONLY valid JSON in this exact format (no markdown, no code blocks):
{{
    "name": "extracted name",
    "email": "extracted email",
    "phone": "extracted phone",
    "skills": "skill1, skill2, skill3, ...",
    "education": "degree and field",
    "college": "university name",
    "experience": "X years OR Y roles",
    "summary": "brief summary"
}}

If any field cannot be found, use "N/A" as the value.
Return ONLY the JSON object, nothing else.
"""

    model_names = [
        "models/gemini-2.5-flash",     # Fastest
        "models/gemini-2.5-pro",       # Higher accuracy
        "models/gemini-pro-latest",    # Fallback
    ]

    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            ai_response = response.text.strip()
            
            # Clean up response (remove markdown code if present)
            ai_response = re.sub(r'^```json\s*|\s*```$', '', ai_response, flags=re.MULTILINE)
            
            # Parse JSON response
            parsed_data = json.loads(ai_response)
            
            # Ensure all required fields exist
            required_fields = ['name', 'email', 'phone', 'skills', 'education', 'college', 'experience', 'summary']
            for field in required_fields:
                if field not in parsed_data:
                    parsed_data[field] = 'N/A'
            
            # Rename 'phone' to 'mobile_number' for consistency if needed
            if 'phone' in parsed_data:
                parsed_data['mobile_number'] = parsed_data['phone']
            
            return parsed_data

        except Exception:
            # If one model fails (e.g., quota, JSON error), try the next
            continue

    # All models failed
    return None

def parse_resume_from_file(file_path):
    """
    Main parsing function. Extracts text and sends to AI.
    No regex fallback.
    """
    try:
        # Extract text based on file type
        if file_path.endswith('.pdf'):
            text = _extract_text_from_pdf(file_path)
        elif file_path.endswith('.docx'):
            text = _extract_text_from_docx(file_path)
        else:
            return None
        
        if not text or len(text.strip()) < 50:
            return None
        
        # Try AI-powered parsing
        ai_data = _parse_with_gemini(text)
        
        if ai_data:
            return ai_data
        else:
            # AI parsing failed (returned None or threw exception)
            return None
        
    except Exception:
        return None