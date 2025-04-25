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
    
    # Save service account email for later use
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
    Please analyze this job posting HTML content and extract the following information:
    - Company name
    - Job title
    - Company location
    - Job URL
    - Country (extract the country name from the location, e.g., if location is "Munich, Germany" return "Germany")
    - Key takeaways (extract 3-5 important job responsibilities or requirements from the job description, listed concisely)

    Please respond in JSON format without any markdown formatting:
    {{
        "company_name": "...",
        "job_title": "...",
        "location": "...",
        "job_url": "{job_url}",
        "country": "...",
        "key_takeaways": [
            "takeaway 1",
            "takeaway 2",
            "takeaway 3"
        ]
    }}

    Here's the HTML content:
    {html[:3000]}
    """

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    
    try:
        # Check response content
        print("Raw response:", response.text)
        
        # Clean response text
        cleaned_response = response.text.strip()
        
        # Remove any possible markdown formatting
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
        
        # 指定 'Jobs' 分頁
        sheet = client.open_by_key(spreadsheet_id).worksheet('Jobs')  # 修改這行，從 sheet1 改為指定 'Jobs'
        print(f"✅ Successfully connected to spreadsheet")

        # Get all values from job_url column
        job_url_col = column_letter_to_index(column_mapping['job_url'])
        job_links = sheet.col_values(job_url_col)
        last_row = len(job_links) + 1
        print(f"Found last entry at row {len(job_links)}, will add to row {last_row}")

        # Use new date format YYYY/MM/DD
        current_date = datetime.now().strftime("%Y/%m/%d")
        
        # Update date column
        date_col = column_letter_to_index(date_column)
        sheet.update_cell(last_row, date_col, current_date)
        
        # Update company name
        company_col = column_letter_to_index(column_mapping['company_name'])
        sheet.update_cell(last_row, company_col, job_info.get('company_name', ''))
        
        # Update job link
        job_url_col = column_letter_to_index(column_mapping['job_url'])
        sheet.update_cell(last_row, job_url_col, job_info.get('job_url', ''))
        
        # Update job title
        job_title_col = column_letter_to_index(column_mapping['job_title'])
        sheet.update_cell(last_row, job_title_col, job_info.get('job_title', ''))

        # Update job location
        if 'location' in column_mapping:
            location_col = column_letter_to_index(column_mapping['location'])
            sheet.update_cell(last_row, location_col, job_info.get('location', ''))

        # Update job country
        if 'country' in column_mapping:
            country_col = column_letter_to_index(column_mapping['country'])
            sheet.update_cell(last_row, country_col, job_info.get('country', ''))
        
        # Update key takeaways
        if 'key_takeaways' in column_mapping:
            key_takeaways = job_info.get('key_takeaways', [])
            # Add numbers to each takeaway
            numbered_takeaways = [f"{i+1}. {takeaway}" for i, takeaway in enumerate(key_takeaways)] if key_takeaways else []
            takeaways_text = '\n'.join(numbered_takeaways) if numbered_takeaways else ''
            key_takeaways_col = column_letter_to_index(column_mapping['key_takeaways'])
            sheet.update_cell(last_row, key_takeaways_col, takeaways_text)

        # Output location and country information when updating fields
        print(f"- Location: {job_info.get('location', '')}")
        print(f"- Country: {job_info.get('country', '')}")
        print(f"- Key Takeaways: {takeaways_text}")

        print(f"✅ Successfully added data to row {last_row}")
        print(f"Added data:")
        print(f"- Key Takeaways ({column_mapping['key_takeaways']}{last_row}): {takeaways_text}")
        print(f"- Date ({date_column}{last_row}): {current_date}")
        print(f"- Company Name ({column_mapping['company_name']}{last_row}): {job_info.get('company_name', '')}")
        print(f"- Job Link ({column_mapping['job_url']}{last_row}): {job_info.get('job_url', '')}")
        print(f"- Job Title ({column_mapping['job_title']}{last_row}): {job_info.get('job_title', '')}")

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
        "key_takeaways": "D",
        "location": "G",
        "country": "J"
    }
    date_column = "E"
    
    process_job_link(job_url, column_mapping, date_column, spreadsheet_id)
