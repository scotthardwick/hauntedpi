import os, sched, heapq, threading, logging

# get the GPIO Library
try:
    import RPi.GPIO as GPIO
except ImportError:
    logging.warn("!!! Using MOCK GPIO !!!")
    import mock.GPIO as GPIO

# Mixer from pygame for sound
try:
    from pygame import mixer, time
except ImportError:
    logging.warn("!!! Using MOCK GPIO !!!")
    from mock.pygame import mixer, time

PUD_DOWN = GPIO.PUD_DOWN
PUD_UP = GPIO.PUD_UP

RISING = GPIO.RISING
FALLING = GPIO.FALLING

_clock = time.Clock()
_elapsed = 0

_events = []

print "Init IO"
GPIO.setmode(GPIO.BCM)

print "Init sound"
mixer.init()


#_cwd = os.path.dirname(os.path.realpath(__file__))

_q_lock = threading.Semaphore()

def tick():
    global _elapsed

    # look for events to trigger
    while _events:
        event = None
        with _q_lock:
            if _events[0][0] < _elapsed:
                event = heapq.heappop(_events)

        if event != None:
            logging.debug("Triggering event {} {}", event[0], event[1])
            event[1](*event[2], **event[3])
        else:
            break

    # tick clock 10 fps
    _elapsed += _clock.tick(60)

def _create_timer(delay, callback, args=[], kwargs={}):
    event = [(delay*1000)+_elapsed, callback, args, kwargs]
    with _q_lock:
        heapq.heappush(_events, event)
    logging.info("Queue event for {}s - {} {}", delay, event[0], event[1])

def add_input(channel, pull_up_down=PUD_UP):
    """
    Configure a GPIO for input. This function returns the channel so can
    also be used to define constants for each channel

    e.g to define a constant for a push button on GPIO 5
    BUTTON_5 = director.add_input(5)
    """
    # Default to PUD_UP so switch connect to ground
    GPIO.setup(channel, GPIO.IN, pull_up_down=pull_up_down)
    return channel

def add_output(channel, initial=False):
    """
    Configure a GPIO for output. This function returns the channel so can
    also be used to define constants for each channel

    e.g to define a constant for a relay switch on GPIO 5
    RELAY_5 = director.add_output(5)

    You can also optionally pass the inital value
    so the same call with default output HIGH would be
    RELAY_5 = director.add_output(5, True)
    """
    logging.info("Configure output %d", channel)
    GPIO.setup(channel, GPIO.OUT, initial=initial)
    return channel

def set_output(channel, value=True, delay=0, duration=None):
    """
    Sets an output HIGH/LOW. Takes optional delay and duration.
    Passing a duration will reverse the output after duration seconds

    e.g to set GPIO 23 HIGH for 10 seconds in 20 seconds time
    director.set_output(23, 1, 20, 10)
    """
    if delay > 0:
        _create_timer(delay, GPIO.output, (channel, value))
    else:
        GPIO.output(channel, value)

    if ( duration != None ):
        _create_timer(duration+delay, GPIO.output, (channel, not value))

def set_on(channel, delay=0, duration=None):
    """
    Sets an output HIGH. Takes optional delay and duration.
    Passing a duration will turn the output LOW after duration seconds

    e.g to set GPIO 23 HIGH for 10 seconds in 20 seconds time
    director.set_on(23, 20, 10)
    """
    set_output(channel, True, delay, duration)

def set_off(channel, delay=0, duration=None):
    """
    Sets an output LOW. Takes optional delay and duration.
    Passing a duration will turn the output HIGH after duration seconds

    e.g to set GPIO 23 LOW for 10 seconds in 20 seconds time
    director.set_off(23, 20, 10)
    """
    set_output(channel, False, delay, duration)

def add_trigger(channel, callback, args, bouncetime=200, edge=RISING):
    """
    Call a function when an input GPIO is triggered

    e.g to call the function play when GPIO 5 is triggered
    director.add_trigger(5, play, ()))
    """
    def trigger(channel):
        callback(*args)
    GPIO.remove_event_detect(channel)
    GPIO.add_event_detect(channel, edge, callback=trigger, bouncetime=bouncetime)

def schedule(delay, callback, args):
    """
    Schedules a function to be called after the defined delay in seconds

    e.g to call the play function after 10 seconds
    director.schedule(10, play, ())
    """
    _create_timer(delay, callback, args)


def play_sound(sound, delay=None):
    """
    Play the sound at the given file location.
    """
    #sound = os.path.join(_cwd, sound)
    if ( delay != None ):
        _create_timer(delay, play_sound, (sound))
    else:
        logging.info("Playing sound %s", sound)
        mixer.Sound(sound).play()

def cleanup():
    print "Cleanup IO"
    GPIO.cleanup() # cleanup all GPIO
    mixer.quit()


