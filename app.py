from flask import Flask, request, logging
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
from dotenv import load_dotenv
import requests
from parser import parse_resume_from_file  
from sheets_handler import add_resume_to_sheet
import logging



load_dotenv()
app = Flask(__name__)

#logging
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_CLIENT = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)





@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Main webhook endpoint to receive WhatsApp messages
    """
    try:
        sender = request.values.get('From', '')
        num_media = int(request.values.get('NumMedia', 0))
        response = MessagingResponse()
        msg = response.message()
        
        if num_media > 0:
            media_url = request.values.get('MediaUrl0', '')
            media_type = request.values.get('MediaContentType0', '')
            
            if 'pdf' in media_type or 'document' in media_type or 'msword' in media_type:
                file_name = download_media(media_url, media_type)
                
                if file_name:
                    
                    # Parse the resume with AI (no fallback)
                    parsed_data = parse_resume_from_file(file_name)
                    
                    if parsed_data:
                        # Save to Google Sheets
                        success = add_resume_to_sheet(parsed_data, parsing_method="AI-Powered")
                        
                        if success:
                            reply_body = (
                                f"✅ Resume processed successfully!\n\n"
                                f"Name: {parsed_data.get('name', 'N/A')}\n"
                                f"Email: {parsed_data.get('email', 'N/A')}\n"
                                f"Phone: {parsed_data.get('mobile_number', 'N/A')}\n\n"
                                f"Data saved to Google Sheets."
                            )
                            msg.body(reply_body)
                        else:
                            msg.body("Error saving data to Google Sheets. Please contact support.")
                    else:
                        msg.body("Could not parse resume. The file might be empty, corrupt, or an image-based PDF. Please send a valid text-based PDF or DOCX file.")
                    
                    # Clean up downloaded file
                    if os.path.exists(file_name):
                        os.remove(file_name)
                else:
                    msg.body("Error downloading file. Please try again.")
            else:
                msg.body("Please send a resume as a PDF or DOCX file.")
        else:
            # No attachment, send instructions
            msg.body(" Welcome to the Resume Parser Bot!\n\n"
                     "Send me a resume (PDF or DOCX) and I will extract the key details and save them to Google Sheets.")
        
        return str(response)
        
    except Exception as e:
        app.logger.error(f"Webhook Error: {e}")
        response = MessagingResponse()
        msg = response.message()
        msg.body("⚠️ An unexpected error occurred. Please try again later.")
        return str(response)





def download_media(media_url, content_type):
    """
    Download media file from WhatsApp
    """
    try:
        response = requests.get(media_url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
        
        if response.status_code == 200:
            # Determine file extension
            if 'pdf' in content_type:
                file_name = 'temp_resume.pdf'
            else:
                file_name = 'temp_resume.docx'
            
            # Save file
            with open(file_name, 'wb') as f:
                f.write(response.content)
            return file_name
        else:
            app.logger.error(f"Error downloading media: {response.status_code}")
            return None
            
    except Exception as e:
        app.logger.error(f"Error in download_media: {e}")
        return None

if __name__ == '__main__':
    app.run(port=5000, debug=True)