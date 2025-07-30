from PIL import Image, ImageDraw
import time

def generate_display():
    im = Image.new('1', (480, 800), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(im)
    draw.line([(0, 0), (480, 800)], fill=0)
    im.show()

generate_display()
