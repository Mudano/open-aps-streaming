
from oauth2client.service_account import ServiceAccountCredentials
import traceback
import gspread
import sys


class Google:

    def __init__(self, gdrive_key):

        self.gdrive_key = gdrive_key
        self.authorize_key(self.gdrive_key)

    def authorize_key(self, key):

        if hasattr(self, 'gc'):
            del self.gc

        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(key, scope)

        self.gc = gspread.authorize(credentials)

    def select_worksheet(self, worksheet_name=None, worksheet_number=None, all_worksheets=False):

        if worksheet_name:
            self.worksheet = self.sheet.worksheet(worksheet_name)

        if worksheet_number:
            self.worksheet = self.sheet.get_worksheet(worksheet_number)

        if all_worksheets:
            self.worksheet = self.sheet.worksheets()

        if not worksheet_name and worksheet_number and all_worksheets:

            print('You have not provided a worksheet selection parameter.')
            sys.exit(666)

        return self.worksheet

    def retrieve_worksheet(self, worksheet_name=None, worksheet_number=None):

        retry_count = 0
        while retry_count <=5:
            try:
                worksheet = self.select_worksheet(worksheet_name, worksheet_number).get_all_records()
                return worksheet

            except gspread.exceptions.APIError as e:

                if 'Request had invalid authentication credentials' in str(e):

                    self.authorize_key(self.gdrive_key)

                else:
                    raise gspread.exceptions.APIError(traceback.format_exc())

        raise gspread.exceptions.APIError(f'Retries maxed for obtaining spreadsheet with name "{self.sheet.title}" and worksheet "{worksheet_name if worksheet_name else worksheet_number}".')

    def create_worksheet(self, title, row_num, col_num):

        resp = self.sheet.add_worksheet(title, row_num, col_num)

        return resp

    def update_cell(self, cell, new_value, worksheet_name=None, worksheet_number=None):

        sheet = self.select_worksheet(worksheet_name, worksheet_number)
        sheet.update_acell(cell, new_value)

    def get_cell_value(self, cell, worksheet_name=None, worksheet_number=None):

        sheet = self.select_worksheet(worksheet_name, worksheet_number)
        value = sheet.acell(cell).value

        return value

    def get_row_or_column(self, index, row=False, column=False, worksheet_name=None, worksheet_number=None):

        sheet = self.select_worksheet(worksheet_name, worksheet_number)

        if row:
            values = sheet.row_values(index)

        elif column:
            values = sheet.col_values(index)

        else:
            print('You have not specified whether you want to select a row/column.')
            sys.exit(666)

        return values

    def share_spreadsheet(self, email):

        self.sheet.share(email, perm_type='user', role='writer')

    def add_target_spreadsheet(self, spreadsheet_url):

        self.spreadsheet_url = spreadsheet_url
        self.sheet = self.gc.open_by_url(spreadsheet_url)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
