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

# title_font = ImageFont.load(os.path.join(font_dir, 'ncenB18.pil'))
title_font = ImageFont.truetype(os.path.join(font_dir, 'ManufacturingConsent-Regular.ttf'), size=35)
#summary_font = ImageFont.load(os.path.join(font_dir, 'helvR18.pil'))
summary_font = ImageFont.truetype(os.path.join(font_dir, 'gothamrnd_medium.otf'), size=20)
#date_font = ImageFont.load(os.path.join(font_dir, 'helvR24.pil'))
date_font = ImageFont.truetype(os.path.join(font_dir, 'gothamrnd_medium.otf'), size=31)
#date_day_font = ImageFont.load(os.path.join(font_dir, 'helvR10.pil'))
date_day_font = ImageFont.truetype(os.path.join(font_dir, 'gothamrnd_book.otf'), size=14)
#weather_font = ImageFont.load(os.path.join(font_dir, 'helvR14.pil'))
weather_font = ImageFont.truetype(os.path.join(font_dir, 'gothamrnd_medium.otf'), size=20)
#time_font = ImageFont.load(os.path.join(font_dir, 'helvR14.pil'))
#time_font_bold = ImageFont.load(os.path.join(font_dir, 'helvR18.pil'))
time_font = ImageFont.truetype(os.path.join(font_dir, 'gothamrnd_medium.otf'), size=16)
time_font_bold = ImageFont.truetype(os.path.join(font_dir, 'gothamrnd_bold.otf'), size=18)

TITLE_SEPERATOR_HEIGHT = 130
VIRTICLE_DATE_SEPERATOR = 53
EVENT_SUMMARY_WRAP_LENGTH = WIDTH - 2*VIRTICLE_DATE_SEPERATOR - 35
WEATHER_SEPERATOR_HEIGHT = 600

def generate_display():
    im = Image.new('1', (480, 800), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(im)

    if not internet_available():
        draw_centered_text(draw, "No internet!", title_font, 0, WIDTH, 150)
        return im

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
    downloaded_weather = download_weather()
    draw_weather(im, draw, downloaded_weather)

    return im

def draw_weather(im, draw, downloaded_weather):
    x = 20
    for weather in downloaded_weather[:4]:
        draw_weather_card(im, draw, x, WEATHER_SEPERATOR_HEIGHT + 35, weather, weather_font)
        x += 110

def draw_weather_card(im, draw, x,y, weather, font):
    icon = Image.open(os.path.join(weather_icon_dir, weather['icon'] + ".png"))
    im.paste(icon, (x, y + 20))

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
            if y+45 > WEATHER_SEPERATOR_HEIGHT:
                return
            draw_event(draw, event, y)
            y += 55 # 45 + 10

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
    draw.text((WIDTH - 15 - end_len, y+22), end, font=time_font)

if __name__ == "__main__":
    im = generate_display()
    im.show()
