from PIL import Image, ImageDraw, ImageFont

from datetime import datetime, time

from weather import download_weather
from cal import get_calendar_events
from util import internet_available

import os
import logging


WIDTH = 480
HEIGHT = 800

font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
weather_icon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weather-icons')

title_day_font = ImageFont.truetype(os.path.join(font_dir, 'ManufacturingConsent-Regular.ttf'), size=50)
title_font = ImageFont.truetype(os.path.join(font_dir, 'ManufacturingConsent-Regular.ttf'), size=38)
summary_font = ImageFont.truetype(os.path.join(font_dir, 'GothamRnd-Medium-Emoji.ttf'), size=25)
date_font = ImageFont.truetype(os.path.join(font_dir, 'gothamrnd_medium.otf'), size=31)
date_day_font = ImageFont.truetype(os.path.join(font_dir, 'gothamrnd_book.otf'), size=14)
weather_font = ImageFont.truetype(os.path.join(font_dir, 'gothamrnd_medium.otf'), size=24)
time_font = ImageFont.truetype(os.path.join(font_dir, 'gothamrnd_medium.otf'), size=20)
time_font_bold = ImageFont.truetype(os.path.join(font_dir, 'gothamrnd_bold.otf'), size=22)

TITLE_SEPERATOR_HEIGHT = 130
VIRTICLE_DATE_SEPERATOR = 53
EVENT_SUMMARY_WRAP_LENGTH = WIDTH - 2*VIRTICLE_DATE_SEPERATOR - 35
RIGHT_EDGE = WIDTH - 15
WEATHER_SEPERATOR_HEIGHT = 620
EVENT_HEIGHT = 55

def generate_display():
    im = Image.new('1', (480, 800), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(im)

    if not internet_available():
        draw_centered_text(draw, "No internet!", title_font, 0, WIDTH, 150)
        return im

    # Draw title.
    draw_title(draw)

    # Title seperator.
    # draw.line([(70, TITLE_SEPERATOR_HEIGHT), (WIDTH - 70, TITLE_SEPERATOR_HEIGHT)], width=3)

    # Vertical date seperator
    draw.line([(VIRTICLE_DATE_SEPERATOR, TITLE_SEPERATOR_HEIGHT + 20 ), (VIRTICLE_DATE_SEPERATOR, WEATHER_SEPERATOR_HEIGHT - 20)], width=2)

    # Draw text wrap position
    # draw.line([(VIRTICLE_DATE_SEPERATOR+15+EVENT_SUMMARY_WRAP_LENGTH, TITLE_SEPERATOR_HEIGHT), (VIRTICLE_DATE_SEPERATOR+15+EVENT_SUMMARY_WRAP_LENGTH, HEIGHT)], width=3)

    # Calendar stuff
    events = get_calendar_events()
    draw_calendar_events(draw, events)

    # Weather seperator
    # draw.line([(70, WEATHER_SEPERATOR_HEIGHT), (WIDTH - 70, WEATHER_SEPERATOR_HEIGHT)], width=2)
    downloaded_weather = download_weather()
    draw_weather(im, draw, downloaded_weather)

    return im

def draw_weather(im, draw, downloaded_weather):
    x = 20
    for weather in downloaded_weather[:4]:
        draw_weather_card(im, draw, x, WEATHER_SEPERATOR_HEIGHT + 15, weather, weather_font)
        x += 110

def draw_weather_card(im, draw, x,y, weather, font):
    icon = Image.open(os.path.join(weather_icon_dir, weather['icon'] + ".png"))
    im.paste(icon, (x, y + 25))

    t = weather['time']
    time_x = x + icon.size[0]/2 - font.getlength(t)/2
    draw.text((time_x, y), weather['time'], font=font)

    temp = weather['temperature'] + "°C"
    temp_x = x + icon.size[0]/2 - font.getlength(temp)/2
    draw.text((temp_x, y+115),temp, font=font)

def draw_title(draw):
    today = datetime.today()
    day_ending = {1: 'st', 2: 'nd', 3: 'rd', 21: 'st', 22: 'nd', 23: 'rd', 31: 'st'}.get(today.day, 'th')

    day = today.strftime('%A')
    date = today.strftime('The ' + str(today.day) + day_ending +' of %B %Y')

    draw_centered_text(draw, day, title_day_font, 0, WIDTH, 24)
    draw_centered_text(draw, date, title_font, 0, WIDTH, 82)

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
        if y+EVENT_HEIGHT+10 > WEATHER_SEPERATOR_HEIGHT:
            return
        draw_date(draw, day, y)
        for event in events:
            if y+EVENT_HEIGHT > WEATHER_SEPERATOR_HEIGHT:
                return
            draw_event(draw, event, y)
            y += EVENT_HEIGHT

def draw_date(draw, day, y):
    draw.text((6,y), day.strftime('%d'), font=date_font)
    draw.text((7,y+30), day.strftime('%a'), font=date_day_font)

def draw_event(draw, event, y):
    start = event['start']
    end = event['end']
    if (start.time() <= time(minute=1)) and (end.time() >= time(hour=23, minute=59)):
        # All day events.
        if event['end'].date() > event['start'].date():
            # Handle multiday events.
            start_text = start.strftime('%a %d')
            end_text = end.strftime('%a %d')
        else:
            start_text = ""
            end_text  = ""
    else:
        # Normal events.
        start_text = start.strftime('%H:%M')
        if end.date() > start.date():
            # Handle multiday events.
            end_text = end.strftime('%H:%M (%a %d)')
        else:
            end_text = end.strftime('%H:%M')

    x_pos = VIRTICLE_DATE_SEPERATOR + 15
    start_len = time_font_bold.getlength(start_text)
    end_len = time_font.getlength(end_text)
    wrap_len = RIGHT_EDGE - max(start_len, end_len) - x_pos
    draw_wrapped_text(draw, x_pos, y, event['summary'], summary_font, wrap_len)
    draw.text((RIGHT_EDGE - start_len, y), start_text, font=time_font_bold)
    draw.text((RIGHT_EDGE - end_len, y+26), end_text, font=time_font)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    im = generate_display()
    im.show()
