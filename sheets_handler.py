import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def setup_google_sheets():
    """Set up connection to Google Sheets"""
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'credentials.json', 
        scope
    )
    
    client = gspread.authorize(creds)
    sheet_id = os.getenv('GOOGLE_SHEET_ID')
    spreadsheet = client.open_by_key(sheet_id)
    worksheet = spreadsheet.sheet1
    
    return worksheet

def add_resume_to_sheet(resume_data, parsing_method="AI"):
    """
    Add parsed resume data to Google Sheet
    
    Args:
        resume_data: Dictionary with extracted data
        parsing_method: "AI" or "Regex" to track how it was parsed
    """
    try:
        worksheet = setup_google_sheets()
        
        # Define headers
        headers = ['Name', 'Email', 'Phone', 'Skills', 'Education', 'Experience', 
                  'College', 'Parsing Method', 'Date Added']
        
        # Check if headers exist
        try:
            existing_headers = worksheet.row_values(1)
            if not existing_headers or existing_headers != headers:
                worksheet.insert_row(headers, 1)
                print("✅ Headers added to Google Sheet")
        except Exception:
            worksheet.append_row(headers)
            print("✅ Headers added to Google Sheet")
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Add resume data as new row
        row_data = [
            resume_data.get('name', 'N/A'),
            resume_data.get('email', 'N/A'),
            resume_data.get('mobile_number', resume_data.get('phone', 'N/A')),
            resume_data.get('skills', 'N/A'),
            resume_data.get('education', 'N/A'),
            resume_data.get('experience', 'N/A'),
            resume_data.get('college', 'N/A'),
            parsing_method,
            timestamp
        ]
        
        worksheet.append_row(row_data)
        print(f"✅ Successfully added resume for {resume_data.get('name')} to Google Sheet!")
        return True
        
    except Exception as e:
        print(f"❌ Error adding to sheet: {e}")
        import traceback
        traceback.print_exc()
        return False
