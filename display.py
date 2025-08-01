from PIL import Image, ImageDraw, ImageFont

from datetime import datetime, timedelta, time, date

from caldav.davclient import get_davclient
from caldav.lib.error import NotFoundError

import os
import logging

import creds

WIDTH = 480
HEIGHT = 800

font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')

logging.basicConfig(level=logging.DEBUG)

summary_font = ImageFont.load(os.path.join(font_dir, 'helvR18.pil'))
date_font = ImageFont.load(os.path.join(font_dir, 'helvR24.pil'))
date_day_font = ImageFont.load(os.path.join(font_dir, 'helvR10.pil'))
time_font = ImageFont.load(os.path.join(font_dir, 'helvR14.pil'))
time_font_bold = ImageFont.load(os.path.join(font_dir, 'helvB14.pil'))


# draw_centered_text draws the given text in the center of the bounds x1 and x2
def draw_centered_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, x1:int, x2:int ,y:int):
    text_length = font.getlength(text)
    x = x1 + (x2-x1)/2 - text_length/2
    draw.text((x, y), text, font=font)

TITLE_SEPERATOR_HEIGHT = 80
VIRTICLE_DATE_SEPERATOR = 53

def generate_display():
    font24 = ImageFont.truetype(os.path.join(font_dir, 'Font.ttc'), 24)
    huristica24 = ImageFont.truetype(os.path.join(font_dir, 'Heuristica-Bold.otf'), 24)
    bitmap = ImageFont.load(os.path.join(font_dir, 'ncenB18.pil'))

    im = Image.new('1', (480, 800), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(im)

    # Draw todays date.
    draw_centered_text(draw, todays_date(), bitmap, 0, WIDTH, 35)

    # Title seperator.
    draw.line([(0, TITLE_SEPERATOR_HEIGHT), (WIDTH, TITLE_SEPERATOR_HEIGHT)], width=3)

    # Vertical date seperator
    draw.line([(VIRTICLE_DATE_SEPERATOR, TITLE_SEPERATOR_HEIGHT), (VIRTICLE_DATE_SEPERATOR, HEIGHT)], width=3)

    # Calendar stuff
    events = get_calendar_events()
    display_events(draw, events)


    return im

def display_events(draw, all_events):
    y = TITLE_SEPERATOR_HEIGHT 
    for day, events in all_events:
        y += 10
        display_date(draw, day, y)
        for event in events:
            display_event(draw, event, y)
            y += 40
            if y > HEIGHT - 150:
                return


def display_date(draw, day, y):
    draw.text((6,y), day.strftime('%d'), font=date_font)
    draw.text((7,y+30), day.strftime('%a'), font=date_day_font)

def display_event(draw, event, y):
    draw.text((VIRTICLE_DATE_SEPERATOR + 15, y), event['summary'], font=summary_font)
    if (event['start'] <= time(minute=1)) and (event['end'] >= time(hour=23, minute=59)):
        start = ""
        end  = ""
    else:
        start = event['start'].strftime('%H:%M')
        end = event['end'].strftime('%H:%M')
    start_len = time_font_bold.getlength(start)
    end_len = time_font.getlength(end)
    draw.text((WIDTH - 15 - start_len, y), start, font=time_font_bold)
    draw.text((WIDTH - 15 - end_len, y+15), end, font=time_font)

def todays_date():
    today = datetime.today()
    day_ending = {1: 'st', 2: 'nd', 3: 'rd', 21: 'st', 22: 'nd', 23: 'rd', 31: 'st'}.get(today.day, 'th')
    date = datetime.today().strftime('%A the ' + str(today.day) + day_ending +' of %B %Y')
    return date

def get_calendar_events():
    logging.info("downloading calendar")
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
            end=now+timedelta(days=60),
            event=True,
            expand=True,
        )

        events_by_day = {}
        logging.info("constructing calendar events")
        for event in events:
            e = event.vobject_instance.vevent
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
    print(e.summary.value)
    print(e_start)
    print(e_end)
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

def display_all_fonts():
    im = Image.new('1', (480, 800), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(im)
    y = 0

    for file in os.listdir(font_dir):
        if file.endswith('.pil'):
            font = ImageFont.load(os.path.join(font_dir, file))
            draw.text((0, y), 'hello world my only friend', font=font)
            y += 30

    return im

if __name__ == "__main__":
    im = generate_display()
    im.show()
