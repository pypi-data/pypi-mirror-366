#!/usr/bin/env python3
"""Read from a Google Sheet."""
import os
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


# Get spreadsheet ID from share link
re_sheet_id = re.compile(r"https://docs.google.com/spreadsheets/d/(?P<ID>[\w-]+)", re.DOTALL)


def get_spreadsheet_service():
    """Return the spreadsheet service."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '/Users/lacasta/cl3drv-credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)
    return service


def get_sheet_id(url):
    """Get sheet ID from google sheet url."""
    M = re.search(re_sheet_id, url)
    if M is None:
        print("Wrong url")
        return

    spread_sheet_id = M.group('ID')
    return spread_sheet_id


def get_spreadsheet_data(url, data_range):
    """Get the data from the given range in teh google sheet.

    Args:
        url: google sheet document url
        data_range: the data range, ej. inventory!A2:Z

    """
    service = get_spreadsheet_service()

    spread_sheet_id = get_sheet_id(url)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spread_sheet_id,
                                range=data_range).execute()
    values = result.get('values', [])
    return values


if __name__ == "__main__":
    import json
    tb = get_spreadsheet_data("https://docs.google.com/spreadsheets/d/10_CcIKD8IQ69uRLuITuzqSx4oETc1e0ugynOPlruFTE/edit#gid=97165881", "R0 modules")
#    tb = get_spreadsheet_data("https://docs.google.com/spreadsheets/d/1_h4jXYvFp77ax2YceoDx50fQ9ufzK85aTRkqEfmIKgo/edit#gid=0", 'inventory!A189:Z')
    print(json.dumps(tb, indent=2))
