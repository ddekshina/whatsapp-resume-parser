from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
from dotenv import load_dotenv
import requests
from resume_parser import parse_resume
from sheets_handler import add_resume_to_sheet

load_dotenv()

app = Flask(__name__)

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route('/webhook', methods=['GET'])
def webhook_verify():
    """
    Webhook verification endpoint
    WhatsApp will call this to verify your webhook URL
    """
    # For basic testing, just return 200
    return "Webhook is working!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Main webhook endpoint to receive WhatsApp messages
    """
    try:
        # Get incoming message data
        incoming_msg = request.values.get('Body', '').lower()
        sender = request.values.get('From', '')
        num_media = int(request.values.get('NumMedia', 0))
        
        # Create response object
        response = MessagingResponse()
        msg = response.message()
        
        # Check if there are attachments (resume files)
        if num_media > 0:
            # Get the media URL
            media_url = request.values.get('MediaUrl0', '')
            media_type = request.values.get('MediaContentType0', '')
            
            # Check if it's a PDF or document
            if 'pdf' in media_type or 'document' in media_type:
                # Download the file
                file_name = download_media(media_url)
                
                # In the webhook() function, update the parsing section:

                if file_name:
                    # Parse the resume with AI
                    parsed_data = parse_resume(file_name, use_ai=True)
                    
                    if parsed_data:
                        # Determine which parsing method was used
                        parsing_method = "AI-Powered" if 'summary' in parsed_data else "Regex-Based"
                        
                        # Save to Google Sheets
                        success = add_resume_to_sheet(parsed_data, parsing_method)
                        
                        if success:
                            msg.body(f"✅ Resume received and processed!\n\n"
                            f"🤖 Parsed using: {parsing_method}\n"
                            f"Name: {parsed_data.get('name', 'N/A')}\n"
                            f"Email: {parsed_data.get('email', 'N/A')}\n"
                            f"Phone: {parsed_data.get('mobile_number', 'N/A')}\n\n"
                            f"Data saved to Google Sheets!")


                        else:
                            msg.body("❌ Error saving to Google Sheets. Please try again.")
                    else:
                        msg.body("❌ Could not parse resume. Please send a valid PDF or DOCX file.")
                    
                    # Clean up downloaded file
                    if os.path.exists(file_name):
                        os.remove(file_name)
                else:
                    msg.body("❌ Error downloading file. Please try again.")
            else:
                msg.body("📄 Please send a PDF or DOCX resume file.")
        else:
            # No attachment, send instructions
            msg.body("👋 Welcome to Resume Parser Bot!\n\n"
                    "📤 Send me a resume (PDF or DOCX) and I'll:\n"
                    "1. Extract the key details\n"
                    "2. Save them to Google Sheets\n\n"
                    "Try sending a resume now!")
        
        return str(response)
        
    except Exception as e:
        print(f"Error in webhook: {e}")
        response = MessagingResponse()
        msg = response.message()
        msg.body("⚠️ Something went wrong. Please try again later.")
        return str(response)

def download_media(media_url):
    """
    Download media file from WhatsApp
    """
    try:
        # Download the file
        response = requests.get(media_url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
        
        if response.status_code == 200:
            # Determine file extension
            content_type = response.headers.get('Content-Type', '')
            if 'pdf' in content_type:
                file_name = 'temp_resume.pdf'
            else:
                file_name = 'temp_resume.docx'
            
            # Save file
            with open(file_name, 'wb') as f:
                f.write(response.content)
            
            return file_name
        else:
            print(f"Error downloading media: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error in download_media: {e}")
        return None

if __name__ == '__main__':
    app.run(port=5000, debug=True)
