from __future__ import print_function
import pickle
import os.path
import sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
import time
import datetime

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

def main():

    creds = None
    if os.path.exists('upload_drive_token.pickle'):
        with open('upload_drive_token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'gdrive_credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('upload_drive_token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%H:%M')

    file_metadata = {
        'name': 'RHHI-perf-results' + sys.argv[2] + st,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    file = service.files().create(body=file_metadata).execute()
    folder_id = file.get('id')


    # Call the Drive v3 API
    file_metadata = {'name': sys.argv[2], 'parents': [folder_id]}
    media = MediaFileUpload(sys.argv[1],
                            mimetype='application/zip')
    file = service.files().create(body=file_metadata, media_body=media).execute()

if __name__ == '__main__':
    main()