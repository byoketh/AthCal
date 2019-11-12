try:
    from config import *
    print("config file imported")
except ModuleNotFoundError:
    print('\33[31m' + 'Err: config.py was not found' + '\033[0m')
import requests
import pickle
from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from bs4 import BeautifulSoup
# from datetime import datetime

cell_sportURL = 0
cell_sport = 0
datecell = 34
typecell = 35
timecell = 36
oppocell = 37
locacell = 38
name = list_sport[cell_sport]
UIDnum = 0
UIDnum_prefix = 1000

# HTML request/parse
print("Connecting...")
try:
    page = requests.get(list_sportURL[cell_sportURL])
except ConnectionRefusedError:
    print("Connection refused")


if str(page) == "<Response [200]>":
    print("Connected")
else:
    print("Connection timed out")


rawhtml = BeautifulSoup(page.content, 'html.parser')

# OAuth 2.0 Setup
scopes = ['https://www.googleapis.com/auth/calendar']
flow = InstalledAppFlow.from_client_secrets_file('client_secret_THS.json', scopes=scopes)

# ONLY RUN FIRST TIME:
#credentials = flow.run_console()
#pickle.dump(credentials, open("token.pkl", "wb"))

credentials = pickle.load(open("token.pkl", "rb"))
service = build("calendar", "v3", credentials=credentials)

#Define new_event function
def func_new_event():
    global datecell, timecell, locacell, typecell, oppocell, UIDnum, UIDnum_prefix, cell_sportURL, cell_sport, name
    name = list_sport[cell_sport]
    date = rawhtml.find_all('td')[datecell].get_text()
    time = rawhtml.find_all('td')[timecell].get_text()
    if date == '':
        end_of_schedule = "End of %s Schedule" % (name)
        print(end_of_schedule)
        datecell = 34
        typecell = 35
        timecell = 36
        oppocell = 37
        locacell = 38
        UIDnum = 0
        UIDnum_prefix += 1000
        cell_sportURL += 1
        cell_sport += 1
        name = list_sport[cell_sport]
    else:
        location = rawhtml.find_all('td')[locacell].get_text()
        type = rawhtml.find_all('td')[typecell].get_text()
        year = date.split(' ')[3]
        day = date.split(' ')[2]
        day = day[:-1]
        day = '%02d' % int(day)
        day = str(day)
        month = date.split(' ')[1]
        if month == 'Jan':
            month = '01'
        elif month == 'Feb':
            month = '02'
        elif month == 'Mar':
            month = '03'
        elif month == 'Apr':
            month = '04'
        elif month == 'May':
            month = '05'
        elif month == 'Jun':
            month = '06'
        elif month == 'Jul':
            month = '07'
        elif month == 'Aug':
            month = '08'
        elif month == 'Sep':
            month = '09'
        elif month == 'Oct':
            month = '10'
        elif month == 'Nov':
            month = '11'
        elif month == 'Dec':
            month = '12'
        #Assign/format time variables
        time = time[:-1]
        if time[1] == ':':
            time = '0' + time
        if time[:2] == 'TB':
            datecell += 9
            typecell += 9
            timecell += 9
            oppocell += 9
            locacell += 9
            print("Skipped event with TBA date")
        else:
            try:
                hour = int(time[:2])
            except ValueError:
                func_end_of_schedule()
            meridian = time[5:]
            #Special-case '12AM' -> 0, '12PM' -> 12 (not 24)
            if (hour == 12):
                hour = 0
            if (meridian == 'PM'):
                hour += 12
            time = "%02d" % hour + time[2:8]
            time = time[:-2]
            #Put all time related variables together
            finaldate = year + "-" + month + "-" + day + "T" + time + ":00.000-05:00"
            starttime = finaldate
            changehour = int(finaldate[11:-16])
            changehour += 2
            endtime = finaldate[:11] + str(changehour) + finaldate[13:]
            #Format location
            location = location[:-1]
            #Format type
            type = type[:-1]
            #Create title
            title = name + " " + location + " " + type
            #Define event iCalUID
            UIDfull = UIDnum_prefix + UIDnum
            UID = str(UIDfull)
            event = {
              'summary': title,
              'location': location,
              'organizer': {
                'email': 'thsathcal@gmail.com',
                'displayName': 'CHLAthCal'
              },
              'start': {
                'dateTime': starttime
              },
              'end': {
                'dateTime': endtime
              },
              'iCalUID': UID
            }
            imported_event = service.events().import_(calendarId='primary', body=event).execute()
            print ("Event imported ID: " + imported_event['id'])
            datecell += 9
            typecell += 9
            timecell += 9
            oppocell += 9
            locacell += 9
            UIDnum += 1

while True:
    func_new_event()

print("END")
