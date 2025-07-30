from PIL import Image, ImageDraw

def generate_display():
    im = Image.new('1', (480, 800), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(im)
    draw.line([(0, 0), (480, 800)], fill=0)

    return im

if __name__ == "__main__":
    im = generate_display()
    im.show()
