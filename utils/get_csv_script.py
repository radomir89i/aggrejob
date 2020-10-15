from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from googleapiclient.discovery import build
import io
import os
import pandas as pd
from sqlalchemy import create_engine


SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = '../credentials.json'
FOLDER_ID = '1HrUEphX1chXTYCr7k2DsX6Q8viDxd2as'
CREDENTIALS = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
DB_CONN = 'top_secret_info'
service = build('drive', 'v3', credentials=CREDENTIALS)

result = service \
    .files() \
    .list(
        pageSize=1000,
        fields='nextPageToken, files(id, name, mimeType)') \
    .execute()['files']


def get_csv_files(path=os.getcwd()):

    """
    Gets all *.csv files from Google Drive folder and puts them in folder with given path (current folder by default).
    :param path: path to folder where downloaded files should be placed
    :return: None
    """

    for file in result:
        if file['mimeType'] == 'text/csv':
            request = service.files().get_media(fileId=file['id'])
            fh = io.FileIO(os.path.join(path, file['name']), 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print("Download %d%%." % int(status.progress() * 100))


def load_from_csv_to_database(path=os.getcwd()):

    """
    Loads all *.csv files from given folder to database.
    :param path: path to *csv files folder
    :return: None
    """

    engine = create_engine(DB_CONN)
    files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.csv')]
    for file in files:
        data = pd.read_csv(file)
        data.to_sql('vacancy', engine, if_exists='append', index=False)


if __name__ == '__main__':
    get_csv_files()
    load_from_csv_to_database()