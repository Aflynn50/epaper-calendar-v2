from PIL import Image, ImageDraw, ImageFont

from datetime import datetime, timedelta, time, date

from caldav.davclient import get_davclient
from caldav.lib.error import NotFoundError

from weather import download_weather

import os
import logging

import creds

WIDTH = 480
HEIGHT = 800

font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
weather_icon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weather-icons')

logging.basicConfig(level=logging.DEBUG)

title_font = ImageFont.load(os.path.join(font_dir, 'ncenB18.pil'))
summary_font = ImageFont.load(os.path.join(font_dir, 'helvR18.pil'))
date_font = ImageFont.load(os.path.join(font_dir, 'helvR24.pil'))
date_day_font = ImageFont.load(os.path.join(font_dir, 'helvR10.pil'))
weather_font = ImageFont.load(os.path.join(font_dir, 'helvR14.pil'))
time_font = ImageFont.load(os.path.join(font_dir, 'helvR14.pil'))
time_font_bold = ImageFont.load(os.path.join(font_dir, 'helvR18.pil'))



TITLE_SEPERATOR_HEIGHT = 105
VIRTICLE_DATE_SEPERATOR = 53
EVENT_SUMMARY_WRAP_LENGTH = WIDTH - 2*VIRTICLE_DATE_SEPERATOR - 35
CALENDAR_END_HEIGHT = 600
WEATHER_SEPERATOR_HEIGHT = 575

def generate_display():
    im = Image.new('1', (480, 800), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(im)

    # Draw todays date.
    draw_centered_text(draw, todays_date(), title_font, 0, WIDTH, 50)

    # Title seperator.
    # draw.line([(70, TITLE_SEPERATOR_HEIGHT), (WIDTH - 70, TITLE_SEPERATOR_HEIGHT)], width=3)

    # Vertical date seperator
    draw.line([(VIRTICLE_DATE_SEPERATOR, TITLE_SEPERATOR_HEIGHT + 20 ), (VIRTICLE_DATE_SEPERATOR, WEATHER_SEPERATOR_HEIGHT - 5)], width=2)

    # Draw text wrap position
    # draw.line([(VIRTICLE_DATE_SEPERATOR+15+EVENT_SUMMARY_WRAP_LENGTH, TITLE_SEPERATOR_HEIGHT), (VIRTICLE_DATE_SEPERATOR+15+EVENT_SUMMARY_WRAP_LENGTH, HEIGHT)], width=3)

    # Calendar stuff
    events = get_calendar_events()
    draw_calendar_events(draw, events)

    # Weather seperator
    # draw.line([(70, WEATHER_SEPERATOR_HEIGHT), (WIDTH - 70, WEATHER_SEPERATOR_HEIGHT)], width=2)

    draw_weather_card(im, draw, 20, WEATHER_SEPERATOR_HEIGHT + 40, {'time': "10:30", 'icon':"wi-cloud", "temperature": "12"}, weather_font)

    return im

def draw_weather_card(im, draw, x,y, weather, font):
    icon = Image.open(os.path.join(weather_icon_dir, weather['icon'] + ".png"))

    im.paste(icon, (x, y + 15))

    t = weather['time']
    time_x = x + icon.size[0]/2 - font.getlength(t)/2
    draw.text((time_x, y), weather['time'], font=font)

    temp = weather['temperature'] + "°C"
    temp_x = x + icon.size[0]/2 - font.getlength(temp)/2
    draw.text((temp_x, y+110),temp, font=font)

def todays_date():
    today = datetime.today()
    day_ending = {1: 'st', 2: 'nd', 3: 'rd', 21: 'st', 22: 'nd', 23: 'rd', 31: 'st'}.get(today.day, 'th')
    date = datetime.today().strftime('%A the ' + str(today.day) + day_ending +' of %B %Y')
    return date

def draw_wrapped_text(draw, x, y, text, font, wrap_length):
    if font.getlength(text) <= wrap_length:
        draw.text((x, y), text, font=font)
        return
    text = text[:-1]
    while font.getlength(text + "...") > wrap_length:
        text = text[:-1]
    draw.text((x, y), text + "...", font=font)

# draw_centered_text draws the given text in the center of the bounds x1 and x2.
def draw_centered_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, x1:int, x2:int ,y:int):
    text_length = font.getlength(text)
    x = x1 + (x2-x1)/2 - text_length/2
    draw.text((x, y), text, font=font)

def draw_calendar_events(draw, all_events):
    y = TITLE_SEPERATOR_HEIGHT
    for day, events in all_events:
        y += 10
        draw_date(draw, day, y)
        for event in events:
            if y+40 > WEATHER_SEPERATOR_HEIGHT:
                return
            draw_event(draw, event, y)
            y += 50

def draw_date(draw, day, y):
    draw.text((6,y), day.strftime('%d'), font=date_font)
    draw.text((7,y+30), day.strftime('%a'), font=date_day_font)

def draw_event(draw, event, y):
    draw_wrapped_text(draw, VIRTICLE_DATE_SEPERATOR + 15, y, event['summary'], summary_font, EVENT_SUMMARY_WRAP_LENGTH)

    if (event['start'] <= time(minute=1)) and (event['end'] >= time(hour=23, minute=59)):
        start = ""
        end  = ""
    else:
        start = event['start'].strftime('%H:%M')
        end = event['end'].strftime('%H:%M')
    start_len = time_font_bold.getlength(start)
    end_len = time_font.getlength(end)
    draw.text((WIDTH - 15 - start_len, y), start, font=time_font_bold)
    draw.text((WIDTH - 15 - end_len, y+25), end, font=time_font)

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

if __name__ == "__main__":
    im = generate_display()
    im.show()
