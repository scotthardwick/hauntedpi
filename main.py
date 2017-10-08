#!/usr/bin/python

import signal, os, glob, imp, sys, threading, logging
import director

#Console Only Logging
#logging.basicConfig(level=logging.DEBUG)

#File Only Logging
#logging.basicConfig(
    #filename="/home/pi/hauntedpi/test.log",
    #level=logging.DEBUG,
    #format="%(asctime)s:%(levelname)s:%(message)s"
    #)
#logger = logging.getLogger(__name__)

# Console and File Logging
logging_format = "%(asctime)s:%(levelname)s:%(message)s"
logging.basicConfig(level=logging.DEBUG, format=logging_format)
logger = logging.getLogger(__name__)
 
# create a file handler
handler = logging.FileHandler("/home/pi/hauntedpi/test.log")

# create a logging format
formatter = logging.Formatter(logging_format)
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

def load_scenes():
    """
    Load all py files in scene directory
    """
    
    logger.info("Resetting Director")
    director.reset()

    _cwd = os.path.dirname(os.path.realpath(__file__)) if len(sys.argv) < 2 else sys.argv[1]
    scenename = os.path.join(_cwd, "scenes/")
    logger.info("Loading Scenes from %s", scenename)
    scenes = glob.glob(os.path.join(_cwd, "scenes/scene_*.py"))

    # Lets also reload contstants
    scenes.insert(0, os.path.join(_cwd, "scenes/constants.py"))

    for file_path in scenes:
        logger.info("Loading Scene %s", file_path)
        mod_name,file_ext = os.path.splitext(os.path.split(file_path)[-1])
        try:
            del sys.modules[mod_name]
        except KeyError:
            pass
        scene_mod = imp.load_source(mod_name, file_path)

def process_keyboard():
    try:
        while True:
            channel = sys.stdin.readline()
            try:
                channel = int(channel)
                director.trigger(channel)
            except ValueError:
                if channel == "r\n":
                    load_scenes()
                else:
                    pass
    except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
        logger.debug("Exiting HauntedPi Thread")

# setup a thread to monitor key input
key_thread = threading.Thread(target=process_keyboard)
key_thread.daemon = True
key_thread.start()

# handle SIGTERM
def terminate(signum, frame):
    raise KeyboardInterrupt()
signal.signal(signal.SIGTERM, terminate)

# Load the scenes
load_scenes()

logger.info("Press CTRL+C to exit")
try:
    while 1:
        director.tick()

except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    logger.debug("Control-C Pressed on Keyboard.")

finally:
    director.cleanup()

