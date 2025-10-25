# whatsapp-resume-parser

## Introduction

This project is a Python-based application designed to parse resume files submitted via WhatsApp and store the extracted information in a Google Sheet. It utilizes AI for enhanced resume analysis and integrates with various services like Twilio and Google Sheets to achieve its functionality.

## Problem Statement

The project aims to automate the process of collecting and organizing resume data. By allowing users to submit resumes through WhatsApp, the application parses the data using AI and stores it in a structured format in Google Sheets, thereby simplifying the recruitment process.

## Features

*   **WhatsApp Integration:** Receives resume files (PDF and DOCX) from users via WhatsApp.
*   **Resume Parsing:** Extracts key information from uploaded resumes using AI-powered analysis and file type handling (PDF and DOCX).
*   **Data Storage:**  Stores parsed resume data in a Google Sheet.
*   **Error Handling:** Includes mechanisms to manage potential errors during file processing, AI API calls, and Google Sheets interaction.
*   **File Handling:** Downloads, saves, and deletes uploaded resume files.
*   **Webserver exposure:** Exposes the local development environment to the internet for testing webhooks using `ngrok`.

## How It Works (Implementation Overview)

1.  **Incoming WhatsApp Messages:** The application receives incoming messages via a webhook endpoint (`/webhook`) exposed through Twilio.
2.  **File Download and Processing:** Upon receiving a resume, the application downloads the file. The `parser.parse_resume_from_file` function is then called to extract the text and key information from the resume. The `parser.py` module uses `google-generativeai` and `PyPDF2`/`docx` to parse and extract the information.
3.  **Data Storage in Google Sheets:** The extracted resume data is then sent to the `sheets_handler.py` module. The `sheets_handler.add_resume_to_sheet` function formats and appends the resume data to a specified Google Sheet.
4.  **Google Sheets Interaction:**  `sheets_handler.py` uses the `gspread` library and a service account, set up with the help of a credentials file loaded by the  `oauth2client.service_account` dependency to connect to the Google Sheet. It also handles header management, adding headers if they are missing.
5.  **Webserver and Tunneling:** The `start_ngrok.py` script opens a secure tunnel using `ngrok` to expose a local webserver running on port 5000, allowing the application to receive WhatsApp webhooks.  The `/webhook` endpoint receives the incoming requests.
6.  **Configuration:** Environment variables (`GOOGLE_SHEET_ID`, `GEMINI_API_KEY`, `NGROK_AUTHTOKEN`, Twilio credentials) are used for configuration.

## Tech Stack

*   **Programming Language:** Python
*   **Libraries:**
    *   `Flask`: Web framework.
    *   `Twilio`: For WhatsApp integration.
    *   `google.generativeai`: Google's AI SDK for interacting with Gemini models.
    *   `gspread`: Google Sheets API.
    *   `oauth2client.service_account`: Authentication with Google Sheets.
    *   `requests`: HTTP requests.
    *   `ngrok`: Creates secure tunnels.
    *   `python-dotenv`: Loads environment variables.
    *   `PyPDF2`: PDF parsing.
    *   `docx` (python-docx): DOCX parsing.
    *   `os`: Operating system interaction.
    *   `json`: Working with JSON data.
    *   `re`: Regular expressions.
    *   `datetime`: Timestamping data.
    *   `logging`: Error logging.

## Getting Started 

1.  **Setting up Google Sheets Credentials:**  Ensure a `credentials.json` file is present for Google Sheets authentication.
2.  **Setting up Environment Variables:** Configure the necessary environment variables (e.g., `GOOGLE_SHEET_ID`, `GEMINI_API_KEY`, `NGROK_AUTHTOKEN`, Twilio credentials).  These are loaded from a `.env` file.
3.  **Install dependencies:** Ensure `requirements.txt` is installed using `pip install -r requirements.txt`.
4.  **Run ngrok:** Execute `start_ngrok.py` to create a secure tunnel and expose the local web server.

## Conclusion

The whatsapp-resume-parser project provides a streamlined solution for collecting, parsing, and organizing resume data from WhatsApp. By leveraging AI, webhooks, and Google Sheets integration, it automates the process of resume management, making it easier for recruiters to collect and organize information from potential candidates. The project's modular design and reliance on configuration files enhance its flexibility and maintainability.