from display import generate_display
from waveshare import epd7in5_V2
from PIL import Image
import logging
from datetime import datetime, time

logging.basicConfig(level=logging.INFO)

def main():
    logging.info("GENERATING E-PAPER DISPLAY AT: " + datetime.now().strftime("%X %x"))
    im = generate_display()
    im = im.transpose(Image.ROTATE_180)

    try:
        logging.info("epd7in5_V2 display refresh")
        epd = epd7in5_V2.EPD()

        now = datetime.now().time()
        logging.info("Init and Clear")
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
