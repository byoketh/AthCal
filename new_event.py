#Installation
#pip install google-api-python-client
#pip install google_auth_oauthlib

# OAuth 2.0 Setup
from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
scopes = ['https://www.googleapis.com/auth/calendar']
flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', scopes=scopes)
# ONLY RUN FIRST TIME:
#credentials = flow.run_console()
import pickle
# ONLY RUN FIRST TIME:
#pickle.dump(credentials, open("token.pkl", "wb"))
credentials = pickle.load(open("token.pkl", "rb"))
service = build("calendar", "v3", credentials=credentials)

print(Setup Complete!)

#Creates an event
event = {
  'summary': 'Leaving',
  'location': 'THS',
  'organizer': {
    'email': 'rdcordrey@gmail.com',
    'displayName': 'Richie'
  },
  'start': {
    'dateTime': '2011-06-03T10:00:00.000-07:00'
  },
  'end': {
    'dateTime': '2011-06-03T10:25:00.000-07:00'
  },
  'iCalUID': 'originalUID'
}

imported_event = service.events().import_(calendarId='primary', body=event).execute()

print (imported_event['id'])
