import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv
from datetime import datetime
import logging

load_dotenv()

def setup_google_sheets():
    """Set up connection to Google Sheets"""
    try:
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
    except Exception as e:
        logging.error(f"Failed to setup Google Sheets: {e}")
        return None

def add_resume_to_sheet(resume_data, parsing_method="AI"):
    """
    Add parsed resume data to Google Sheet
    """
    try:
        worksheet = setup_google_sheets()
        if worksheet is None:
            return False
            
        headers = ['Name', 'Email', 'Phone', 'Skills', 'Education', 'Experience', 
                  'College', 'Summary', 'Parsing Method', 'Date Added']
        
        # Check if headers exist, add if not
        try:
            existing_headers = worksheet.row_values(1)
            if not existing_headers or existing_headers != headers:
                worksheet.insert_row(headers, 1)
        except gspread.exceptions.APIError: # Handle empty sheet
            worksheet.append_row(headers)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        row_data = [
            resume_data.get('name', 'N/A'),
            resume_data.get('email', 'N/A'),
            resume_data.get('mobile_number', resume_data.get('phone', 'N/A')), # Use mobile_number or phone
            resume_data.get('skills', 'N/A'),
            resume_data.get('education', 'N/A'),
            resume_data.get('experience', 'N/A'),
            resume_data.get('college', 'N/A'),
            resume_data.get('summary', 'N/A'), # Added Summary field
            parsing_method,
            timestamp
        ]
        
        worksheet.append_row(row_data)
        return True
        
    except Exception as e:
        logging.error(f"Error adding to sheet: {e}")
        return False