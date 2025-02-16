# Job Posting Auto-fill to Google Sheets

This project automatically extracts job posting information from web pages and fills it into a specified Google Sheets document.

## Features

- Automatic job posting webpage content extraction
- Uses Google Gemini AI to parse job information
- Automatic filling of specified Google Sheets fields
- Supports multiple job information fields (company name, job title, location, etc.)

## Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Google Cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![Google Sheets](https://img.shields.io/badge/Google_Sheets-34A853?style=for-the-badge&logo=google-sheets&logoColor=white)
![Gemini AI](https://img.shields.io/badge/Gemini_AI-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Environment Variables](https://img.shields.io/badge/Environment_Variables-ECD53F?style=for-the-badge&logo=.env&logoColor=black)
![REST APIs](https://img.shields.io/badge/REST_APIs-FF6C37?style=for-the-badge&logo=postman&logoColor=white)

### Key Libraries

- `google-generativeai`: Google Gemini AI integration
- `gspread`: Google Sheets API wrapper
- `google-auth`: Google authentication
- `python-dotenv`: Environment variables management
- `requests`: HTTP requests handling

## Requirements

1. Python 3.7+
2. Required Python packages:
   ```bash
   pip install google-generativeai requests gspread google-auth python-dotenv
   ```

## Setup

1. Copy `.env.example` to `.env`:

   ```bash
   cp .env.example .env
   ```

2. Set required environment variables in `.env`:

   - `GEMINI_API_KEY`: Google Gemini API key
   - `GOOGLE_CREDENTIALS_FILE`: Path to Google Service Account credentials file
   - `SPREADSHEET_ID`: Your Google Sheets document ID

3. Set up Google Sheets API:
   - Create a project in Google Cloud Console
   - Enable Google Sheets API and Google Drive API
   - Create a service account and download credentials file
   - Add the service account email to your Google Sheets sharing list

## Usage

```bash
python autofill-google-sheet.py <job_url>
```

Example:

```bash
python autofill-google-sheet.py "https://example.com/job/123"
```

## Important Notes

- Ensure `.env` file is properly configured and not uploaded to version control
- Make sure Google Sheets is properly shared with the service account
- The spreadsheet ID can be found in the Google Sheets URL

## Expected Spreadsheet Format

The script expects the following column structure:

- Column E: Date
- Column F: Company Name
- Column G: Country
- Column H: Job URL
- Column I: Job Title

## License

[Add your license terms here]

## Contributing

[Add your contribution guidelines here]
