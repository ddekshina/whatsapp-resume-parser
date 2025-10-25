import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import PyPDF2
from docx import Document
import re
import os

# Import Gemini parser
try:
    from gemini_resume_parser import parse_resume_with_gemini, estimate_gemini_cost
    AI_AVAILABLE = True
    print("✅ Gemini AI parser available")
except ImportError:
    AI_AVAILABLE = False
    print("⚠️ AI parser not available, using regex-based extraction")

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def extract_text_from_docx(docx_path):
    """Extract text from DOCX file"""
    try:
        doc = Document(docx_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return ""

def extract_email(text):
    """Extract email from text using regex"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else 'N/A'

def extract_phone(text):
    """Extract phone number from text with improved patterns"""
    text_clean = text.replace('\n', ' ').replace('\r', ' ')
    
    phone_patterns = [
        r'\+91[\s-]?\d{5}[\s-]?\d{5}',
        r'\+91[\s-]?\d{10}',
        r'\b\d{5}[\s-]?\d{5}\b',
        r'\b\d{10}\b',
        r'\+\d{1,3}[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}',
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    ]
    
    for pattern in phone_patterns:
        phones = re.findall(pattern, text_clean)
        if phones:
            phone = phones[0].strip()
            phone = re.sub(r'\s+', ' ', phone)
            return phone
    
    return 'N/A'

def extract_name(text):
    """Extract name from first few lines"""
    lines = text.split('\n')
    
    for line in lines[:5]:
        line = line.strip()
        if line and len(line.split()) >= 2 and len(line.split()) <= 4:
            if line[0].isupper() and not any(char.isdigit() for char in line):
                keywords = ['resume', 'curriculum', 'vitae', 'cv', 'profile', 'summary']
                if not any(keyword in line.lower() for keyword in keywords):
                    return line
    
    return 'N/A'

def parse_resume_regex_fallback(text):
    """Fallback regex-based parser if AI fails"""
    print("📋 Using regex-based parser (fallback)...")
    
    parsed_data = {
        'name': extract_name(text),
        'email': extract_email(text),
        'mobile_number': extract_phone(text),
        'skills': 'N/A',
        'education': 'N/A',
        'experience': 'N/A',
        'college': 'N/A'
    }
    
    return parsed_data

def parse_resume(file_path, use_ai=True):
    """
    Parse resume using Gemini AI with regex fallback.
    
    Args:
        file_path: Path to resume file (PDF or DOCX)
        use_ai: Whether to use AI parser (default: True)
    
    Returns:
        Dictionary with extracted data
    """
    try:
        print(f"📄 Parsing file: {file_path}")
        
        # Extract text based on file type
        if file_path.endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        elif file_path.endswith('.docx'):
            text = extract_text_from_docx(file_path)
        else:
            print("❌ Unsupported file format")
            return None
        
        if not text or len(text.strip()) < 50:
            print("❌ Could not extract sufficient text from file")
            return None
        
        print(f"✅ Extracted {len(text)} characters of text")
        
        # Try AI-powered parsing first
        if use_ai and AI_AVAILABLE:
            # Estimate cost (Gemini is free!)
            cost = estimate_gemini_cost(len(text))
            print(f"💰 AI cost: ${cost:.4f} (Gemini Pro is FREE!)")
            
            ai_data = parse_resume_with_gemini(text)
            
            if ai_data:
                # AI succeeded, ensure mobile_number field exists
                if 'phone' in ai_data and 'mobile_number' not in ai_data:
                    ai_data['mobile_number'] = ai_data['phone']
                
                print(f"✅ AI parsed successfully!")
                return ai_data
            else:
                print("⚠️ AI parsing failed, falling back to regex")
        
        # Fallback to regex-based parsing
        regex_data = parse_resume_regex_fallback(text)
        return regex_data
        
    except Exception as e:
        print(f"❌ Error parsing resume: {e}")
        import traceback
        traceback.print_exc()
        return None
