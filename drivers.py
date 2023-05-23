import logging
import os
from typing import List, Iterable

import psycopg2
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError

from server.settings import SERVICE_ACCOUNT_FILE, SPREADSHEETS_ID, DATABASES

logger = logging.getLogger(__name__)


class SpreadsheetsModule:
    def __init__(self, table_name):
        credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
        self._spreadsheets = build('sheets', 'v4', credentials=credentials)
        self._sheets_id = SPREADSHEETS_ID
        self._table = table_name
        self._create_table_if_not_exist()

    def _create_table_if_not_exist(self) -> None:
        try:
            spreadsheet = self._spreadsheets.spreadsheets().get(spreadsheetId=self._sheets_id).execute()
            sheets_list = spreadsheet.get('sheets')
            exist = False
            for sheet in sheets_list:
                if self._table == sheet['properties']['title']:
                    exist = True
                    break
            if not exist:
                self._create_table()
                self._write_headers()
        except HttpError as e:
            logger.info(e)

    def _create_table(self) -> None:
        logger.info(f"Creating table with name --> {self._table}")
        body = {
            'requests': [{
                'addSheet': {
                    'properties': {
                        'title': self._table,
                    }
                }
            }]
        }
        self._spreadsheets.spreadsheets().batchUpdate(
            spreadsheetId=self._sheets_id,
            body=body
        ).execute()

    def _write_headers(self) -> None:
        values = [("URL", 'PROFILE_NAME', "PHONE_NUMBER", 'TITLE', "PRICE",
                   "MILEAGE", "IMG_URL", "IMAGE_COUNT")]
        value_body = {
            'majorDimension': "ROWS",
            'values': values
        }
        self._spreadsheets.spreadsheets().values().append(
            spreadsheetId=self._sheets_id,
            range=self._table,
            valueInputOption="USER_ENTERED",
            body=value_body
        ).execute()

    def add_data_to_table(self, data: List[Iterable]) -> None:
        value_body = {
            'majorDimension': "ROWS",
            'values': data
        }
        self._spreadsheets.spreadsheets().values().append(
            spreadsheetId=self._sheets_id,
            range=self._table,
            valueInputOption="USER_ENTERED",
            body=value_body
        ).execute()

    def clear_table(self):
        self._spreadsheets.spreadsheets().values().clear(
            spreadsheetId=self._sheets_id,
            range=self._table
        ).execute()


class DBDumper:

    def __init__(self):
        self._db = DATABASES['default']
        self.command = 'pg_dump -h {host} -p {port} -U {user} -d {dbname} > {path}'.format(
            dbname=self._db['NAME'],
            host=self._db['HOST'],
            user=self._db['USER'],
            password=self._db['PASSWORD'],
            port=self._db['PORT'],
            path="db_dump.sql"
        )

    def get_dump_file(self):
        try:
            os.system(self.command)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    d = DBDumper()
    d.get_dump_file()