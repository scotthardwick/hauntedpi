import director, random, logging
from constants import *
logger = logging.getLogger(__name__)

# Setup ambient track to loop indefinitely in background
director.play_sound("scenes/audio/marketplace_1.wav", volume=0.5, delay=0, loops=-1, origin="Thunder")

