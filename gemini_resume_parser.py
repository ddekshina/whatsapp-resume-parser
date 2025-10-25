import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def parse_resume_with_gemini(text):
    """
    Use Google Gemini AI to extract resume information, with three-model fallback.
    Order: 2.5-flash → 2.5-pro → pro-latest
    """
    print("🤖 Using Google Gemini AI to parse resume...")

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
        "models/gemini-2.5-flash",     # Fastest and most quota-friendly
        "models/gemini-2.5-pro",       # Higher accuracy, slightly more quota use
        "models/gemini-pro-latest",    # Latest fallback if quota or error on others
    ]

    for model_name in model_names:
        try:
            print(f"🔄 Trying Gemini model: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            ai_response = response.text.strip()

            print(f"✅ Gemini AI Response received using {model_name}")
            # Clean up response (remove markdown code if present, just in case)
            ai_response = ai_response.replace('``````', '').strip()
            
            # Parse JSON response
            parsed_data = json.loads(ai_response)
            required_fields = ['name', 'email', 'phone', 'skills', 'education', 'college', 'experience', 'summary']
            for field in required_fields:
                if field not in parsed_data:
                    parsed_data[field] = 'N/A'
            print(f"✅ Gemini parsed data successfully with {model_name}!")
            return parsed_data

        except Exception as e:
            print(f"❌ Model {model_name} failed: {e}")
            continue

    print("❌ All Gemini models failed, using regex fallback!")
    return None

def parse_from_gemini_text(ai_text):
    """
    Fallback: Extract data from Gemini's natural language response
    """
    data = {
        'name': 'N/A',
        'email': 'N/A',
        'phone': 'N/A',
        'skills': 'N/A',
        'education': 'N/A',
        'college': 'N/A',
        'experience': 'N/A',
        'summary': 'N/A'
    }
    lines = ai_text.split('\n')
    for line in lines:
        line_lower = line.lower()
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip().strip('"').strip()
            if 'name' in key:
                data['name'] = value
            elif 'email' in key:
                data['email'] = value
            elif 'phone' in key or 'mobile' in key:
                data['phone'] = value
            elif 'skill' in key:
                data['skills'] = value
            elif 'education' in key or 'degree' in key:
                data['education'] = value
            elif 'college' in key or 'university' in key or 'institute' in key:
                data['college'] = value
            elif 'experience' in key:
                data['experience'] = value
            elif 'summary' in key:
                data['summary'] = value
    return data

def estimate_gemini_cost(text_length):
    """
    Gemini models are free for the current demo/assignment usage.
    """
    return 0.0  # No cost for reasonable quotas
