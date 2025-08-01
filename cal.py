import logging

from caldav.davclient import get_davclient
from caldav.lib.error import NotFoundError

from datetime import datetime, timedelta, time, date

import creds

def get_calendar_events():
    downloaded_events = download_events()

    logging.info("constructing calendar events")
    return construct_events(downloaded_events)

def download_events():
    logging.info("downloading calendar: " + creds.CALDAV_URL)
    with get_davclient(username=creds.CALDAV_USERNAME, password=creds.CALDAV_PASSWORD, url=creds.CALDAV_URL) as client:
        my_principal = client.principal()
        try:
            my_calendar = my_principal.calendar()
            logging.info("calendar was found")
        except NotFoundError:
            logging.error("cannot fetch calendar")
            return []
        now = datetime.now()
        events = my_calendar.search(
            start=datetime.now(),
            end=now+timedelta(days=30),
            event=True,
            expand=True,
        )
        return events

# Group the events by day and split multiday events accross days.
def construct_events(downloaded_events):
    events_by_day = {}
    for event in downloaded_events:
        e = event.vobject_instance.vevent
        logging.info("processing event: " + e.summary.value + " " + str(e.dtstart.value) + " " + str(e.dtend.value))
        if type(e.dtstart.value) is datetime:
            if type(e.dtend.value) is not datetime:
                logging.error("event start is datetime but end is " + str(type(e.dtend.value)))
                return {}
            add_datetime_event(events_by_day, e)
        elif type(e.dtstart.value) is date:
            if type(e.dtend.value) is not date:
                logging.error("event start is date but end is " + str(type(e.dtend.value)))
                return {}
            add_date_event(events_by_day, e)

    logging.info("sorting events")
    for day, events in events_by_day.items():
        events_by_day[day] = sorted(events, key=lambda d: d['start'])
    sorted_events = sorted(events_by_day.items())
    return sorted_events

def add_date_event(dict, e):
    e_start = e.dtstart.value
    e_end = e.dtend.value
    while e_start != (e_end - timedelta(days=1)):
        add_event(dict, e_start, e.summary.value, time.min, time.max)
        e_start = e_start + timedelta(days=1)
    add_event(dict, e_start, e.summary.value, time.min, time.max)

def add_datetime_event(dict, e):
    e_start = e.dtstart.value
    e_end = e.dtend.value
    while e_start.date() != e_end.date():
        add_event(dict, e_start.date(), e.summary.value, e_start.time(), time.max)
        # Get the start of the next day.
        e_start = e_start.replace(hour=0,minute=0,second=0,microsecond=0) + timedelta(days=1)
    add_event(dict, e_start.date(), e.summary.value, e_start.time(), e_end.time())

def add_event(dict, date, summary, start, end):
    if date >= datetime.now().date():
        if date in dict:
            dict[date].append({'summary':summary,'start': start,'end': end})
        else:
            dict[date] = [{'summary':summary,'start': start,'end': end}]
