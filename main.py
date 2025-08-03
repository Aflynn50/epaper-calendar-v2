from display import generate_display
from waveshare import epd7in5_V2
from PIL import Image
import logging
from datetime import datetime, time

logging.basicConfig(level=logging.INFO)

def main():
    im = generate_display()
    im = im.transpose(Image.ROTATE_180)

    try:
        logging.info("epd7in5_V2 Demo")
        epd = epd7in5_V2.EPD()

        now = datetime.now().time()
        if  now > time(hour=1) and now < time(hour=3): # Reset the display in the early hours of the morning.
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
