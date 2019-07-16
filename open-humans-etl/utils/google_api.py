
from oauth2client import file
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import sys


class Google:
    def __init__(self, gdrive_key, spreadsheet_name=None, spreadsheet_key=None, spreadsheet_url=None):

        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(gdrive_key, scope)

        self.gc = gspread.authorize(credentials)

        if spreadsheet_name:
            self.sheet = self.gc.open(spreadsheet_name)

        elif spreadsheet_key:
            self.sheet = self.gc.open_by_key(spreadsheet_key)

        elif spreadsheet_url:
            self.sheet = self.gc.open_by_url(spreadsheet_url)

        elif not spreadsheet_name and not spreadsheet_key and not spreadsheet_url:

            print('You have not provided a spreadsheet selection parameter.')
            sys.exit(666)

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

        worksheet = self.select_worksheet(worksheet_name, worksheet_number).get_all_records()

        return worksheet

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

        values = None
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
