from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os

WIDTH = 480
HEIGHT = 800

font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')

# draw_centered_text draws the given text in the center of the bounds x1 and x2
def draw_centered_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, x1:int, x2:int ,y:int):
    text_length = font.getlength(text)
    x = x1 + (x2-x1)/2 - text_length/2
    draw.text((x, y), text, font=font)

def generate_display():
    font24 = ImageFont.truetype(os.path.join(font_dir, 'Font.ttc'), 24)
    huristica24 = ImageFont.truetype(os.path.join(font_dir, 'Heuristica-Bold.otf'), 24)
    bitmap = ImageFont.load(os.path.join(font_dir, 'ncenR18.pil'))

    im = Image.new('1', (480, 800), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(im)

    draw_centered_text(draw, todays_date(), bitmap, 0, WIDTH, 15)

    # Title seperator
    draw.line([(0, 60), (WIDTH, 60)], width=4)


    return im

def todays_date():
    today = datetime.today()
    day_ending = {1: 'st', 2: 'nd', 3: 'rd', 21: 'st', 22: 'nd', 23: 'rd', 31: 'st'}.get(today.day, 'th')
    date = datetime.today().strftime('%A the %-m' + day_ending +' of %B %Y')
    return date


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
