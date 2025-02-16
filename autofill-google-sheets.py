import google.generativeai as genai
import requests
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json 
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Google Gemini API Key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

# Connect to Google Sheets API
def connect_to_google_sheets():
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    credentials = Credentials.from_service_account_file(
        os.getenv('GOOGLE_CREDENTIALS_FILE'),  # Read credentials file path from environment variables
        scopes=SCOPES
    )
    
    # Store service account email for later use
    global SERVICE_ACCOUNT_EMAIL
    SERVICE_ACCOUNT_EMAIL = credentials.service_account_email
    
    client = gspread.authorize(credentials)
    return client

# Fetch job page HTML
def fetch_job_page(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"❌ Unable to access URL, status code: {response.status_code}")
        return None

# Parse job information using Google Gemini
def extract_job_info(html, job_url):
    prompt = f"""
    This is the HTML content of a job posting page. Please parse the following information:
    - Company name
    - Job title
    - Company location
    - Job URL
    - Country (extract the country name from the location info, e.g., if location is "Munich, Germany" return "Germany")

    Please respond directly in JSON format without any markdown formatting:
    {{
        "company_name": "...",
        "job_title": "...",
        "location": "...",
        "job_url": "{job_url}",
        "country": "..."
    }}

    Here is the HTML content:
    {html[:3000]}
    """

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    
    try:
        # Check response content
        print("Raw response:", response.text)
        
        # Clean response text
        cleaned_response = response.text.strip()
        
        # Remove all possible markdown formatting
        if "```" in cleaned_response:
            start = cleaned_response.find("{")
            end = cleaned_response.rfind("}") + 1
            if start != -1 and end != -1:
                cleaned_response = cleaned_response[start:end]
        
        cleaned_response = cleaned_response.strip()
        print("Cleaned response:", cleaned_response)
        
        # Parse JSON
        result = json.loads(cleaned_response)
        return result
    except json.JSONDecodeError as e:
        print(f"❌ AI response format error, unable to parse: {e}")
        print(f"Attempted to parse text: '{cleaned_response}'")
        return None
    except Exception as e:
        print(f"❌ Other error occurred: {str(e)}")
        return None

# Convert Excel Column letter to number index (A = 1, B = 2, C = 3, ...)
def column_letter_to_index(letter):
    return ord(letter.upper()) - ord('A') + 1

# Insert data into specified Google Sheets fields
def append_to_sheet(job_info, column_mapping, date_column, spreadsheet_id):
    # Clean spreadsheet_id
    if '/' in spreadsheet_id:
        spreadsheet_id = spreadsheet_id.split('/')[0]
    if '?' in spreadsheet_id:
        spreadsheet_id = spreadsheet_id.split('?')[0]
    if '#' in spreadsheet_id:
        spreadsheet_id = spreadsheet_id.split('#')[0]
        
    client = connect_to_google_sheets()
    try:
        print(f"Attempting to connect to spreadsheet...")
        print(f"Using Spreadsheet ID: {spreadsheet_id}")
        sheet = client.open_by_key(spreadsheet_id).sheet1
        print(f"✅ Successfully connected to spreadsheet")

        # Get all values from column H (job link)
        job_links = sheet.col_values(8)  # H is column 8
        last_row = len(job_links) + 1  # Find the next row after the last entry
        print(f"Found last entry at row {len(job_links)}, will add to row {last_row}")

        # Use new date format YYYY/MM/DD
        current_date = datetime.now().strftime("%Y/%m/%d")
        
        # Update each column separately
        # Update column E (date)
        sheet.update_cell(last_row, 5, current_date)  # E is column 5
        
        # Update column F (company name)
        sheet.update_cell(last_row, 6, job_info.get('company_name', ''))  # F is column 6
        
        # Update column H (job link)
        sheet.update_cell(last_row, 8, job_info.get('job_url', ''))  # H is column 8
        
        # Update column I (job title)
        sheet.update_cell(last_row, 9, job_info.get('job_title', ''))  # I is column 9

        # Output location and country information when updating fields
        print(f"- Location: {job_info.get('location', '')}")
        print(f"- Country: {job_info.get('country', '')}")

        print(f"✅ Successfully added data to row {last_row}")
        print(f"Added data:")
        print(f"- Date (E{last_row}): {current_date}")
        print(f"- Company Name (F{last_row}): {job_info.get('company_name', '')}")
        print(f"- Job Link (H{last_row}): {job_info.get('job_url', '')}")
        print(f"- Job Title (I{last_row}): {job_info.get('job_title', '')}")

    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        print(f"Please verify the following:")
        print(f"1. Spreadsheet ID: {spreadsheet_id}")
        print(f"2. Spreadsheet has been shared with: {SERVICE_ACCOUNT_EMAIL}")
        print(f"3. Sharing permissions set to 'Editor'")
        print(f"4. Spreadsheet format is correct")
        return

# Main program: Fetch & Parse & Save to Google Sheets
def process_job_link(job_url, column_mapping, date_column, spreadsheet_id):
    html_content = fetch_job_page(job_url)
    if html_content:
        job_info = extract_job_info(html_content, job_url)
        if job_info:
            append_to_sheet(job_info, column_mapping, date_column, spreadsheet_id)

# Test execution
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python autofill-google-sheet.py <job_url>")
        sys.exit(1)
        
    # Read spreadsheet_id from .env
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    if not spreadsheet_id:
        print("❌ Error: Please set SPREADSHEET_ID in .env file")
        sys.exit(1)
    
    # Read job link
    job_url = sys.argv[1]
    
    # Add some validation for the job URL
    if not job_url.startswith(('http://', 'https://')):
        print("❌ Error: Job URL must start with http:// or https://")
        sys.exit(1)
    
    column_mapping = {
        "company_name": "F",
        "job_title": "I",
        "job_url": "H",
        "country": "G"
    }
    date_column = "E"
    
    process_job_link(job_url, column_mapping, date_column, spreadsheet_id)
