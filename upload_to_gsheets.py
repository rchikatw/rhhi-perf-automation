from __future__ import print_function
import pickle
import os.path
import csv
import sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
"""
cat sysbench-results.out | egrep " cat|threads:|transactions|tps|read/write|min:|avg:|max:" | tr -d "\n" | sed 's/Number of threads: /\n/g' | sed 's/\[/\n/g' | sed 's/[A-Za-z\/]\{1,\}://g'| sed 's/ \.//g' | sed -e 's/read\/write//g'  -e 's/per sec.)//g' -e 's/ms//g' -e 's/(//g' -e 's/^.*cat //g' | sed 's/ \{1,\}/,/g' > sysbench.csv
"""

def main():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('upload_gsheets_token.pickle'):
        with open('upload_gsheets_token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'gsheets_credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('upload_gsheets_token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    spreadsheet_body = {
        'properties': {
            'title': "RHHI-Sysbench-Results"
        }
    }
    request = service.spreadsheets().create(body=spreadsheet_body,fields='spreadsheetId,spreadsheetUrl')
    response = request.execute()
    # print(response.get('spreadsheetId'))
    print(response.get('spreadsheetUrl'))

    values = [
        ['threads','transactions','tps','min','avg','max']
    ]

    body = {
        'values': values
    }
    result = service.spreadsheets().values().append(
        spreadsheetId=response.get('spreadsheetId'), body=body, range="Sheet1!A1:H",valueInputOption="USER_ENTERED").execute()

    data_values=[]
    line_count = 0
    with open(sys.argv[1]) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            data_values.append(row)
            line_count = line_count +1

    body ={
       'values': data_values
    }
    result = service.spreadsheets().values().append(
        spreadsheetId=response.get('spreadsheetId'),
        valueInputOption="USER_ENTERED", body=body, range="Sheet1!A2:H").execute()
    # print('{0} cells appended.'.format(result \
    #                                    .get('updates') \
    #                                    .get('updatedCells')))


if __name__ == '__main__':
    # print ("Ref docs for pre-requisites: https://developers.google.com/sheets/api/quickstart/python")
    # print("Usage: python quickstart.py <input file path>")
    main()