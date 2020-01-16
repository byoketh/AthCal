try:
    from config import *
except ModuleNotFoundError:
    print('\33[31m' + 'Err: config.py was not found' + '\033[0m')

# Define and print version and welcome splash
if dev_mode == 1:
    versionName = versionType + ' ' + 'in developer mode'
elif versionType == 'Stable':
    versionName = ' '
else:
    versionName = versionType

versionFull = versionNum + ' ' + versionName
print('Starting AthCal ' + versionFull + '...')
print()

# Import variables from schedules.py
if dev_mode == 1:
    print("Importing schedule data...")

try:
    from schedules import list_sport, list_sportURL, list_sportCALID, list_length
    if dev_mode == 1:
        print('Schedule data imported successfully')
except ModuleNotFoundError:
    # Throws an error if schedules.py is not present
    print('\33[31m' + 'Err: schedules.py was not found' + '\033[0m')

# Import modules
import requests
import pickle
try:
    from apiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from bs4 import BeautifulSoup
except ModuleNotFoundError:
    # Throws an error if the correct modules are not present
    print('\33[31m' + 'Err: One or more Google Calendar API modules were not found. Consider running install_modules.sh' + '\033[0m')

# Initialize variables
var_break = False
cell_sportURL = 0
cell_sport = 0
cell_sportCALID = 0
cell_length = 0
datecell = 34
typecell = 35
timecell = 36
oppocell = 37
locacell = 38
name = list_sport[cell_sport]
event_length = list_length[cell_length]
UIDnum = 0
UIDnum_prefix = 100

# Initial HTML request/parse
begin_schedule_string = "Connecting to %s schedule..." % (list_sport[cell_sport])
print(begin_schedule_string)
try:
    page = requests.get(list_sportURL[cell_sportURL])
except ConnectionRefusedError:
    print("Connection refused")

if dev_mode == 1:
    if str(page) == "<Response [200]>":
        print("Connected")
    else:
        print("Connection timed out")

rawhtml = BeautifulSoup(page.content, 'html.parser')

# OAuth 2.0 Setup
scopes = ['https://www.googleapis.com/auth/calendar']
flow = InstalledAppFlow.from_client_secrets_file('client_secret_THS.json', scopes=scopes)

# ONLY RUN THESE WHEN ADDING CALENDER ACCOUNT(S) FOR THE FIRST TIME:
#credentials = flow.run_console()
#pickle.dump(credentials, open("token.pkl", "wb"))

credentials = pickle.load(open("token.pkl", "rb"))
service = build("calendar", "v3", credentials=credentials)

def func_create_event():
    global datecell, timecell, locacell, typecell, oppocell, UIDnum, UIDnum_prefix, cell_sport, cell_length, name, var_break, rawhtml, date, time, location
    name = list_sport[cell_sport]
    date = rawhtml.find_all('td')[datecell].get_text()
    time = rawhtml.find_all('td')[timecell].get_text()
    location = rawhtml.find_all('td')[locacell].get_text()
    type = rawhtml.find_all('td')[typecell].get_text()
    year = date.split(' ')[3]
        # If the following error occurs more than one event is on one day, pushing the cell variables ahead by one. 
        # Find the type of event causing the error and add it to the exception "elif date[:-1] in" in func_main()
        # 
        # Exception has occurred: IndexError
        # list index out of range
        #   File "/home/richie/Projects/AthCal/AthCalMain.py", line X, in func_new_event
        #     year = date.split(' ')[3]
        #   File "/home/richie/Projects/AthCal/AthCalMain.py", line X, in <module>
    # Format date/time variables for the API
    day = date.split(' ')[2]
    day = day[:-1]
    day = '%02d' % int(day)
    month = date.split(' ')[1]
    if month == 'Jan':
        monthNum = '01'
    elif month == 'Feb':
        monthNum = '02'
    elif month == 'Mar':
        monthNum = '03'
    elif month == 'Apr':
        monthNum = '04'
    elif month == 'May':
        monthNum = '05'
    elif month == 'Jun':
        monthNum = '06'
    elif month == 'Jul':
        monthNum = '07'
    elif month == 'Aug':
        monthNum = '08'
    elif month == 'Sep':
        monthNum = '09'
    elif month == 'Oct':
        monthNum = '10'
    elif month == 'Nov':
        monthNum = '11'
    elif month == 'Dec':
        monthNum = '12'
    else:
        print("ERR: Date could not be correctly parsed")
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
        UIDnum += 1
        if dev_mode == 1:
            print("Skipped event with TBA date")
    else:
        hour = int(time[:2])
        meridian = time[5:]
        #Special-case '12AM' -> 0, '12PM' -> 12 (not 24)
        if (hour == 12):
            hour = 0
        if (meridian == 'PM'):
            hour += 12
        timeFull = "%02d" % hour + time[2:8]
        timeFull = timeFull[:-2]
        #Daylight Savings Time:)
        if monthNum in ('01','02','12'): #NOT DST
            var_dst = False
        elif monthNum == '03': #START DST
            if int(day) < 8:
                var_dst = False
            elif int(day) >= 8:
                var_dst = True
        elif monthNum == '11': #END DST
            if int(day) >= 1:
                var_dst = False
            if int(day) < 1:
                var_dst = True
        elif monthNum in ('04','05','06','07','08','09','10'): #DST
            var_dst = True
        else:
            print("ERR: Daylight Savings time could not be properly calculated")
        #Put all time related variables together
        if var_dst is True:
            dst = ":00.000-04:00"
        elif var_dst is False:
            dst = ":00.000-05:00"
        day = str(day)
        finaldate = year + "-" + monthNum + "-" + day + "T" + timeFull + dst
        starttime = finaldate
        changehour = int(finaldate[11:-16])
        changehour += list_length[cell_length]
        endtime = finaldate[:11] + str(changehour) + finaldate[13:]
        #Format location
        location = location[:-1]
        #Format type
        type = type[:-1]
        #Create title
        title = name + " " + type
        #Define event iCalUID
        uidFull = UIDnum_prefix + UIDnum
        uidString = str(uidFull)
        event = {
          'summary': title,
          'location': location,
          'start': {
            'dateTime': starttime
          },
          'end': {
            'dateTime': endtime
          },
          'iCalUID': uidString
        }
        # '2qqfnf88phkqtjcuchqneooti0@group.calendar.google.com' is the test calID
        # comment out the line below to simulate importing events without actually adding them to a calendar
        imported_event = service.events().import_(calendarId=list_sportCALID[cell_sportCALID], body=event).execute()
        if dev_mode == 1:
            importString = ("Imported Event UID: " + uidString)
 

def func_end_schedule():
    global datecell, timecell, locacell, typecell, oppocell, UIDnum, UIDnum_prefix, cell_sportURL, cell_sport, cell_sportCALID, cell_length, name, var_break, rawhtml, date, time, location
    end_of_schedule = "Imported %s Schedule" % (name)
    print(end_of_schedule)
    print()
    datecell = 34
    typecell = 35
    timecell = 36
    oppocell = 37
    locacell = 38
    UIDnum = 0
    UIDnum_prefix += 100
    cell_sportURL += 1
    cell_sport += 1
    cell_sportCALID += 1
    cell_length += 1
    # HTML request/parse
    try:
        schedule_string = list_sport[cell_sport]
    except IndexError:
        var_break = True
        return
    begin_schedule_string = "Connecting to %s schedule..." % (schedule_string)
    print(begin_schedule_string)
    page = requests.get(list_sportURL[cell_sportURL])
     
if dev_mode == 1:
    if str(page) == "<Response [200]>":
        print("Connected")
    else:
        print("Connection timed out")

    rawhtml = BeautifulSoup(page.content, 'html.parser')


def func_main():
    global datecell, timecell, locacell, typecell, oppocell, UIDnum, UIDnum_prefix, cell_sportURL, cell_sport, name, rawhtml, date, time, location
    try:
        date = rawhtml.find_all('td')[datecell].get_text()
        time = rawhtml.find_all('td')[timecell].get_text()
    except IndexError:
        func_end_schedule()
    if date == '':
        func_end_schedule()
    elif date[:-1] in ('Match', 'Invitational', 'Double Header', 'Triangular'):
        datecell -= 9
        typecell -= 1
        timecell -= 1
        oppocell -= 1
        locacell -= 1
        func_create_event()
        datecell += 17
        typecell += 9
        timecell += 9
        oppocell += 9
        locacell += 9
    else:
        func_create_event()
        datecell += 9
        typecell += 9
        timecell += 9
        oppocell += 9
        locacell += 9
        UIDnum += 1

while True:
    if dev_mode == True:
        input("Press enter to import an event")
    try:
        func_main()
    except KeyboardInterrupt:
        print('')
        print('The script was aborted')
        break
    if var_break == 1:
        print('')
        print('The scrpit has completed succsessfully')
        break
