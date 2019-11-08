# HTML request/parse
import requests
page = requests.get("https://www.chlathletics.org/g5-bin/client.cgi?cwellOnly=1&G5MID=052119071109056048054057085057079121108097120099075117068089100068089084043048101043098053076105052097056050047110098085078120075090073066076116116112089043067103066054066121048&G5statusflag=view&G5genie=661&G5button=12&vw_worksheet=4087&vw_type=mySchoolOnly&school_id=7")
page
from bs4 import BeautifulSoup
rawhtml = BeautifulSoup(page.content, 'html.parser')

# OAuth 2.0 Setup
from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
scopes = ['https://www.googleapis.com/auth/calendar']
flow = InstalledAppFlow.from_client_secrets_file('client_secret_THS.json', scopes=scopes)

# ONLY RUN FIRST TIME:
#credentials = flow.run_console()
import pickle
# ONLY RUN FIRST TIME:
#pickle.dump(credentials, open("token.pkl", "wb"))
credentials = pickle.load(open("token.pkl", "rb"))
service = build("calendar", "v3", credentials=credentials)

loopbool = True
datecell = 34
typecell = 35
timecell = 36
oppocell = 37
locacell = 38
UIDnum = 0

def func_loop():
    global loopbool, datecell, typecell, timecell, oppocell, locacell, UIDnum
    while loopbool == True:
        datecell += 9
        typecell += 9
        timecell += 9
        oppocell += 9
        locacell += 9
        UIDnum += 1
        func_new_event()

#Define new_event function
def func_new_event():
    global loopbool, datecell, typecell, timecell, oppocell, locacell, UIDnum
    global time, location, type, date
    time = rawhtml.find_all('td')[timecell].get_text()
    location = rawhtml.find_all('td')[locacell].get_text()
    type = rawhtml.find_all('td')[typecell].get_text()
    date = rawhtml.find_all('td')[datecell].get_text()
    if date == '':
        loopbool = False
    elif time == r'TBD\xa0':
        func_loop()
    else:
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
        from datetime import datetime
        time = time[:-1]
        if time[1] == ':':
            time = '0' + time
        if time[:2] == 'TB':
            func_loop()
        hour = int(time[:2])
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
        title = location + " " + type
        #Define event iCalUID
        UID = "UID" + str(UIDnum)
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
        func_loop()


func_new_event()
print("END")
