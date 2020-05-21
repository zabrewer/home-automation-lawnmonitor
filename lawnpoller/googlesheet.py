import gspread
from google.oauth2.service_account import Credentials

# set variables below and
# call this file (python googlesheet.py) to test
# will test API calls to your spreadsheet using test_dict below

# set variables for testing
google_spreadsheet = 'YardMonitor'  # the name of the file/worksheet
google_tabname = 'Backyard1'  # the name of the tab/sheet that you want to write to
# define local file that has API key
apifile = 'client_secret.json'
#define scope for goole API
google_scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

test_dict = {
    'TimeStamp': '18-May-2020 (19:00:19)',
    'PiName': 'FakePi',
    'SensorName': 'FakeSensor',
    'Battery': 99,
    'Temp': 57.2,
    'Moisture': 14,
    'Light': 84,
    'Conductivity': 132
}

# make our connection using credentials in secretfile
def make_cx(secretfile, scopes):
    credentials = Credentials.from_service_account_file(
        filename=secretfile, scopes=scopes)
    g_apicall = gspread.authorize(credentials)
    return g_apicall


def next_row(sheet):
    str_list = list(filter(None, sheet.col_values(1)))
    return str(len(str_list) + 1)


def write_data(secretfile, scopes, filename, worksheetname, sensordata):
    g_apicall = make_cx(secretfile=secretfile, scopes=scopes)
    open_file = g_apicall.open(filename)
    open_wks = open_file.worksheet(worksheetname)
    timestamp = sensordata['TimeStamp']
    pi_name = sensordata['PiName']
    sensorname = sensordata['SensorName']
    battery = sensordata['Battery']
    temp = sensordata['Temp']
    moisture = sensordata['Moisture']
    light = sensordata['Light']
    conductivity = sensordata['Conductivity']
    # find next empty row with function:
    next_emptyrow = next_row(open_wks)
    # update cells in empty row
    open_wks.update_acell("A{}".format(next_emptyrow), timestamp)
    open_wks.update_acell("B{}".format(next_emptyrow), pi_name)
    open_wks.update_acell("C{}".format(next_emptyrow), sensorname)
    open_wks.update_acell("D{}".format(next_emptyrow), battery)
    open_wks.update_acell("E{}".format(next_emptyrow), temp)
    open_wks.update_acell("F{}".format(next_emptyrow), moisture)
    open_wks.update_acell("G{}".format(next_emptyrow), light)
    open_wks.update_acell("H{}".format(next_emptyrow), conductivity)


# if called directly, we use the variables set above and test_dict to test the API call, credentials, etc.
if __name__ == "__main__":
    sensor_1 = write_data(
        secretfile=apifile,
        scopes=google_scope,
        filename=google_spreadsheet,
        worksheetname=google_tabname,
        sensordata=test_dict)