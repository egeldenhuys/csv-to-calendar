from __future__ import print_function
import httplib2
import os
import csv
import json
import sys

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

# try:
#     import argparse
#     flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
# except ImportError:
#     flags = None

flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'CSV to Calendar'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    CALENDAR_NAME = sys.argv[2]

    calendarID = initCalendar(service, CALENDAR_NAME)

    mat = getMatrixFromCSV('timetable.csv')
    events = parseMatrixIntoEvents(mat)

    for x in events:
        uploadEvent(service, x, calendarID)


def deleteAllCalendars_NO(service, summary):
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            if calendar_list_entry['summary'] == summary:
                service.calendars().delete(calendarId=calendar_list_entry['id']).execute()
                # service.calendars().delete('secondaryCalendarId').execute()
                print('Calendar ' + calendar_list_entry['summary'] +' has been deleted')

        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    return None

def getCalendarId(service, calendarSummary):
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            if calendar_list_entry['summary'] == calendarSummary:
                return calendar_list_entry['id']
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    return None

def uploadEvent(service, event, calenderID):
    #print(event)
    print('Creating event... ' + event['summary'] + ' @ ' + event['start']['dateTime'])

    event = service.events().insert(calendarId=calenderID, body=event).execute()
    print('Event created!')

def initCalendar(service, summary):
    calenderID = getCalendarId(service, summary)
    newID = calenderID
    if calenderID != None:
        service.calendars().delete(calendarId=calenderID).execute()
        print('Calendar ' + summary +' has been deleted')

    calendar = {
    'summary': summary,
    'timeZone': 'Africa/Johannesburg'
    }

    created_calendar = service.calendars().insert(body=calendar).execute()

    print('Calendar ' + summary +' has been created')
    newID = created_calendar['id']

    return newID

def getColours(service):
    colors = service.colors().get().execute()

    print(colors)
    # Print available calendarListEntry colors.
    for id, color in colors['calendar']:
        print('colorId: %s'.format(id))
        #print'  Background: %s' % color['background']
        #print '  Foreground: %s' % color['foreground']

    # Print available event colors.
    for id, color in colors['event']:
        print('colorId: %s'.format(id))
        #print '  Background: %s' % color['background']
        #print '  Foreground: %s' % color['foreground']

def createEvent(dayCount, start, duration, subject, location='', colour=''):

    day = 17 + dayCount
    day = int(day)
    hours = start.split(':')[0]
    hours = int(hours)
    hours = hours + duration

    startTime = start
    endTime = '00:00'

    if hours < 10:
        endTime = '0' + str(hours) + ':' + start.split(':')[1]
    else:
        endTime = str(hours) + ':' + start.split(':')[1]

    googleEvent = {
      'summary': subject,
      'location': location,
      'start': {
        'dateTime': '2017-07-' + str(day) + 'T' + str(startTime) + ':00+02:00',
        'timeZone': 'Africa/Johannesburg'
      },
      'end': {
        'dateTime': '2017-07-' + str(day) + 'T' + str(endTime) + ':00+02:00',
        'timeZone': 'Africa/Johannesburg'
      },
      'recurrence': [
        'RRULE:FREQ=WEEKLY;UNTIL=20181102T000000Z'
      ],
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'popup', 'minutes': 15}
        ],
      },
      'colorId': str(colour)
    }

    return googleEvent



def parseMatrixIntoEvents(mat):
    # Row 1: Days ['', 'Monday', '', '', 'Tuesday'...]
    # COLS:
    # 1 (+3): Day
    # Last element on index 13

    # Row 2: Start time, Subject, Location, Colour, Subject...
    # COLS:
    # 0: Start Time
    # 1 (+3): Subject
    # 2 (+3): Location
    # 3 (+3): Colour
    # Last Element on index 15

    # Row 2 -> 12 Times

    # 0 based
    DATA_START_ROW = 2
    DATA_START_COL = 1
    HEADER_ROW = 1
    TIME_COL = 0

    eventList = []

    rowCount = 0

    for row in mat:

        colCount = 0;
        for data in row:

            if rowCount >= DATA_START_ROW:
                if colCount >= DATA_START_COL:
                    if data != '':
                        if mat[HEADER_ROW][colCount] == 'Subject':
                            # Merge entries below
                            duration = 1

                            while (rowCount + duration < len(mat) and mat[rowCount + duration][colCount] == data):
                                mat[rowCount + duration][colCount] = ''
                                duration += 1

                            tmpEntryDict = createEvent((colCount - 1) / 3,
                            mat[rowCount][TIME_COL],
                            duration, data,
                            mat[rowCount][colCount + 1],
                            mat[rowCount][colCount + 2])

                            eventList.append(tmpEntryDict)

            colCount += 1

        rowCount += 1

    return eventList

def getMatrixFromCSV(csvFile):

    rowCount = 0;

    matrix = []

    with open(sys.argv[1], newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            colCount = 0;

            if rowCount >= len(matrix):
                #print('Adding row to matrix')
                matrix.append([])

            for col in row:
                matrix[rowCount].append(col)
                #print('[' + str(rowCount) + '][' + str(colCount) + '] ' + col)
                colCount += 1
            rowCount += 1

    return matrix

if __name__ == '__main__':
    main()
