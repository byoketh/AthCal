# Define and print version and welcome splash
versionNum = '0.9.5'
versionType = 'Alpha'
versionFull = versionNum + ' ' + versionType
print('Starting AthCal ' + versionFull + '...')

# Try to import variables from a config.py file
try:
    from config import list_sport, list_sportURL
except ModuleNotFoundError:
    # Throws an error if config.py is not present
    print('\33[31m' + 'Err: config.py was not found' + '\033[0m')

# Try to import modules
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
var_break = 0
cell_sportURL = 0
cell_sport = 0
datecell = 34
typecell = 35
timecell = 36
oppocell = 37
locacell = 38
name = list_sport[cell_sport]
UIDnum = 0
UIDnum_prefix = 100

# Initial HTML request/parse
print("Connecting to schedule...")
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

def func_create_event():
     global datecell, timecell, locacell, typecell, oppocell, UIDnum, UIDnum_prefix, cell_sportURL, cell_sport, name, var_dst, var_break, rawhtml, date, time, location
     try:
          name = list_sport[cell_sport]
     except IndexError:
          var_break = 1
          return
     date = rawhtml.find_all('td')[datecell].get_text()
     time = rawhtml.find_all('td')[timecell].get_text()
     location = rawhtml.find_all('td')[locacell].get_text()
     type = rawhtml.find_all('td')[typecell].get_text()
     year = date.split(' ')[3]
          # Exception has occurred: IndexError
          # list index out of range
          #   File "/home/richie/Projects/AthCal/AthCalMain.py", line 98, in func_new_event
          #     year = date.split(' ')[3]
          #   File "/home/richie/Projects/AthCal/AthCalMain.py", line 215, in <module>
     day = date.split(' ')[2]
     day = day[:-1]
     day = '%02d' % int(day)
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
     else:
          print("Date could not be parsed")
     #Assign/format time variables
     time = time[:-1]
     if time[1] == ':':
           time = '0' + time
     if time[:2] == 'TB':
          print("Skipped event with TBA date")
          datecell += 9
          typecell += 9
          timecell += 9
          oppocell += 9
          locacell += 9
          UIDnum += 1
     else:
          hour = int(time[:2])
          meridian = time[5:]
          #Special-case '12AM' -> 0, '12PM' -> 12 (not 24)
          if (hour == 12):
               hour = 0
          if (meridian == 'PM'):
               hour += 12
          time = "%02d" % hour + time[2:8]
          time = time[:-2]
          #Daylight Savings Time:
          if month in ('Jan','Feb','Mar','Dec'): #NOT DST
               var_dst = False
          elif month == 'Mar': #START DST
               if day < 10:
                    var_dst = False
               elif day >= 10:
                    var_dst = True
          elif month == 'Nov': #END DST
               if day >= 3:
                    var_dst = False
               if day < 3:
                    var_dst = True
          elif month in ('Apr','May','Jun','Jul','Aug','Sep','Oct'): #DST
               var_dst = True
          else:
               var_dst = True
          #Put all time related variables together
          if var_dst is True:
               dst = ":00.000-04:00"
          elif var_dst is False:
               dst = ":00.000-05:00"
          day = str(day)
          finaldate = year + "-" + month + "-" + day + "T" + time + dst
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
          print ("Imported Event UID: " + str(UIDfull))

def func_end_schedule():
     global datecell, timecell, locacell, typecell, oppocell, UIDnum, UIDnum_prefix, cell_sportURL, cell_sport, name, var_dst, var_break, rawhtml, date, time, location
     end_of_schedule = "End of %s Schedule" % (name)
     print(end_of_schedule)
     datecell = 34
     typecell = 35
     timecell = 36
     oppocell = 37
     locacell = 38
     UIDnum = 0
     UIDnum_prefix += 100
     cell_sportURL += 1
     cell_sport += 1
     # HTML request/parse
     try:
          page = requests.get(list_sportURL[cell_sportURL])
     except IndexError:
          return
     
     print("Connecting to schedule...")
     if str(page) == "<Response [200]>":
          print("Connected")
     else:
          print("Connection timed out")
     rawhtml = BeautifulSoup(page.content, 'html.parser')


def func_main():
     global datecell, timecell, locacell, typecell, oppocell, UIDnum, UIDnum_prefix, cell_sportURL, cell_sport, name, var_dst, var_break, rawhtml, date, time, location
     try:
          date = rawhtml.find_all('td')[datecell].get_text()
          time = rawhtml.find_all('td')[timecell].get_text()
     except IndexError:
          func_end_schedule()
     if date == '':
          func_end_schedule()
     elif date[:-1] in ('Match', 'Invitational', 'Double Header'):
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
     # input("Press Enter To Add Another Event")
     try:
         func_main()
     except KeyboardInterrupt:
         print('Script Aborted')
         break
     if var_break == 1:
         print('')
         print('Scrpit Completed Succsessfully')
         break
