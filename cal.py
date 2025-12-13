import logging

from caldav.davclient import get_davclient
from caldav.lib.error import NotFoundError

from datetime import datetime, timedelta, time, date

import creds

todays_date = datetime.now().date()

def get_calendar_events():
    downloaded_events = download_events()

    logging.info("constructing calendar events")
    return construct_events(downloaded_events)

def download_events():
    logging.info("downloading calendar: " + creds.CALDAV_URL)
    with get_davclient(username=creds.CALDAV_USERNAME, password=creds.CALDAV_PASSWORD, url=creds.CALDAV_URL) as client:
        try:
            my_calendars = client.principal().calendars()
            logging.info("calendars found")
            now = datetime.now()
            events = []
            for my_calendar in my_calendars:
                if my_calendar.id in creds.CALDAV_CALENDAR_IDS:
                    logging.info("fetching events from caledar: " + my_calendar.id)
                    events += my_calendar.search(
                        start=now,
                        end=now+timedelta(days=30),
                        event=True,
                        expand=True,
                    )
        except NotFoundError as e:
            logging.error("cannot fetch calendar: " + str(e))
            return []
        return events

# Group the events by day and split multiday events accross days.
def construct_events(downloaded_events):
    events_by_day = {}
    for event in downloaded_events:
        e = event.vobject_instance.vevent
        start = e.dtstart.value
        end = getattr(e, "dtend", e.dtstart).value
        logging.info("processing event: " + e.summary.value + " start time: " + str(start) + " end time:" + str(end))
        # Process all day event and events including a start and end time.
        if type(start) is datetime:
            if type(end) is not datetime:
                logging.error("event start is datetime but end is " + str(type(end)))
                return {}
            add_datetime_event(events_by_day, e.summary.value, start, end)
        elif type(start) is date:
            if type(end) is not date:
                logging.error("event start is date but end is " + str(type(end)))
                return {}
            add_date_event(events_by_day, e.summary.value, start, end)
        else:
            logging.error("skipping unknown event type: " + str(type(start)))

    logging.info("sorting events")
    for day, events in events_by_day.items():
        events_by_day[day] = sorted(events, key=lambda d: d['start'].time())
    sorted_events = sorted(events_by_day.items())
    return sorted_events

def add_date_event(dict, summary, start, end):
    e_start = start
    # With date events an all day event has its end on the next day. Correct that by subtracting a day
    e_end = end - timedelta(days=1)
    if e_start < todays_date:
        e_start = todays_date
    add_event(dict, e_start, summary, datetime.combine(e_start,time.min), datetime.combine(e_end, time.max))

# Add an event including a start and end time.
def add_datetime_event(dict, summary, start, end):
    if start.date() < todays_date:
        start = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
    add_event(dict, start.date(), summary, start, end)

# Add the event if it is in the future.
def add_event(dict, date, summary, start, end):
    if date >= todays_date:
        if date in dict:
            dict[date].append({'summary':summary,'start': start,'end': end})
        else:
            dict[date] = [{'summary':summary,'start': start,'end': end}]
