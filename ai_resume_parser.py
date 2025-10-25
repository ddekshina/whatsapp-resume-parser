import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Initialize OpenAI client (new way for v1.0+)
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def parse_resume_with_ai(text):
    """
    Use OpenAI GPT to extract resume information intelligently.
    Updated for OpenAI API v1.0+
    """
    try:
        print("🤖 Using AI to parse resume...")
        
        # Create a prompt for GPT to extract structured data
        prompt = f"""
You are an expert resume parser. Extract the following information from the resume text below and return it as a JSON object.

Extract these fields:
- name: Full name of the candidate
- email: Email address
- phone: Phone number (with country code if present)
- skills: List of technical and professional skills (as comma-separated string)
- education: Degree(s) and field of study
- college: University/College name
- experience: Years of experience OR number of roles/projects mentioned
- summary: Brief 2-line professional summary

Resume Text:
{text}

Return ONLY valid JSON in this exact format:
{{
    "name": "extracted name",
    "email": "extracted email",
    "phone": "extracted phone",
    "skills": "skill1, skill2, skill3",
    "education": "degree and field",
    "college": "university name",
    "experience": "X years OR Y roles",
    "summary": "brief summary"
}}

If any field is not found, use "N/A" as the value.
"""

        # Call OpenAI API (NEW SYNTAX for v1.0+)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert resume parser that extracts structured data accurately."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        # Get the response (NEW WAY)
        ai_response = response.choices[0].message.content.strip()
        print(f"✅ AI Response received: {ai_response[:100]}...")
        
        # Parse JSON response
        try:
            parsed_data = json.loads(ai_response)
            
            # Ensure all required fields exist
            required_fields = ['name', 'email', 'phone', 'skills', 'education', 'college', 'experience']
            for field in required_fields:
                if field not in parsed_data:
                    parsed_data[field] = 'N/A'
            
            print(f"✅ AI parsed data: {parsed_data}")
            return parsed_data
            
        except json.JSONDecodeError as e:
            print(f"⚠️ AI returned invalid JSON, using fallback parser")
            return parse_from_ai_text(ai_response)
    
    except Exception as e:
        print(f"❌ Error using AI parser: {e}")
        return None

def parse_from_ai_text(ai_text):
    """
    Fallback: Extract data from AI's natural language response
    """
    import re
    
    data = {
        'name': 'N/A',
        'email': 'N/A',
        'phone': 'N/A',
        'skills': 'N/A',
        'education': 'N/A',
        'college': 'N/A',
        'experience': 'N/A'
    }
    
    lines = ai_text.split('\n')
    for line in lines:
        line_lower = line.lower()
        if 'name:' in line_lower:
            data['name'] = line.split(':', 1)[1].strip()
        elif 'email:' in line_lower:
            data['email'] = line.split(':', 1)[1].strip()
        elif 'phone:' in line_lower:
            data['phone'] = line.split(':', 1)[1].strip()
        elif 'skills:' in line_lower:
            data['skills'] = line.split(':', 1)[1].strip()
        elif 'education:' in line_lower:
            data['education'] = line.split(':', 1)[1].strip()
        elif 'college:' in line_lower or 'university:' in line_lower:
            data['college'] = line.split(':', 1)[1].strip()
        elif 'experience:' in line_lower:
            data['experience'] = line.split(':', 1)[1].strip()
    
    return data

def estimate_ai_cost(text_length):
    """
    Estimate the cost of using OpenAI API for this resume.
    GPT-3.5-turbo: ~$0.002 per resume
    """
    tokens = text_length // 4  # Rough estimate: 1 token ≈ 4 characters
    cost_per_1k_tokens = 0.002  # GPT-3.5-turbo pricing
    estimated_cost = (tokens / 1000) * cost_per_1k_tokens
    return estimated_cost
