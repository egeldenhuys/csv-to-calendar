# Timetable
Upload CSV timetable to Google Calendar

## Setup and Usage
1. Follow https://developers.google.com/google-apps/calendar/quickstart/python
    - Place `client_secret.json` in project directory. (Keep this file secret)
2. Modify the `timetable.csv` template using Libreoffice Calc
    - Do not place text outside of the allocated time slots
    - Subjects that have the same name and are vertically adjacent will be merged
    - Colour represents the colour id in Google Calendar (See image below)
3. Run `python upload.py`
    - Will open webpage to get token
    - Token saved in `~/.credentials/calendar-python-quickstart.json`
    - Will parse the csv and upload events accordingly

## Features
### Auth
- Opens browser to get Google OAuth token
- Saves token to `~/.credentials/calendar-python-quickstart.json` for future use (might want to delete this file after use)

### CSV
- Parse from CSV template. See `timetable.csv`
    ```
               | Monday                      | Tuesday   ...
    Start Time | Subject | Location | Colour | Subject | ...
    07:30      | COS 226 | HB 4-1   |    7   | ...
    ...
    17:30
    ```

### Calendar
- Will operate on the calendar named `csv-to-calendar`
- Everytime `upload.py` is run it will be cleared or created if it does not exist

### Events
- Recur weekly until `2017-11-02`
- Notification 15 minutes before each event
- Colour can be specified in `timetable.csv`
    - See the colour Grid

#### Colours
![colour grid](https://eduardopereira.pt/wp-content/uploads/2012/06/google_calendar_api_event_color_chart.png)

## Images
### Before
![csv](https://imgur.com/IuOvv3pl.png)

### After
![calendar](https://imgur.com/sKkVJUDl.png)

## Warning
This script requests Read/Write access to your calendar. If used incorrectly it may delete all the calendars/events on your account.
