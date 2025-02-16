# Job Posting Auto-fill for Google Sheets

A Python script that automatically extracts job posting information and fills it into a Google Sheets document.

## Features

- Extracts job information from any job posting URL
- Automatically identifies:
  - Company name
  - Job title
  - Location
  - Key job responsibilities/requirements
- Fills information into specified Google Sheets columns
- Adds timestamp for each entry

## Prerequisites

- Python 3.7 or higher
- Google Cloud Project with enabled APIs:
  - Google Sheets API
  - Google Drive API
- Google Gemini API key
- Google Service Account credentials

## Setup

1. Clone the repository:

````bash
git clone [

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
````

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
