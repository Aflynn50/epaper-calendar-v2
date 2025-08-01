from display import generate_display
from waveshare import epd7in5_V2
from PIL import Image
import logging

logging.basicConfig(level=logging.DEBUG)

def main():
    im = generate_display()
    im = im.transpose(Image.ROTATE_180)

    try:
        logging.info("epd7in5_V2 Demo")
        epd = epd7in5_V2.EPD()

        logging.info("init and Clear")
        epd.init()
        epd.Clear()

        epd.display(epd.getbuffer(im))

        logging.info("Goto Sleep...")
        epd.sleep()

    except IOError as e:
        logging.info(e)

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd7in5_V2.epdconfig.module_exit(cleanup=True)
        exit()

if __name__ == "__main__":
    main()
