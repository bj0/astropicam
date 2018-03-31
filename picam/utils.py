import queue
import re
import threading
from functools import wraps
from time import sleep


def get_color_from_hex(s):
    """Transform a hex string color to a kivy
    :class:`~kivy.graphics.Color`.
    """
    if s.startswith('#'):
        return get_color_from_hex(s[1:])

    value = [int(x, 16) / 255.
             for x in re.split('([0-9a-f]{2})', s.lower()) if x != '']
    if len(value) == 3:
        value.append(1)
    return value


def get_hex_from_color(color):
    """Transform a kivy :class:`~kivy.graphics.Color` to a hex value::

        >>> get_hex_from_color((0, 1, 0))
        '#00ff00'
        >>> get_hex_from_color((.25, .77, .90, .5))
        '#3fc4e57f'

    .. versionadded:: 1.5.0
    """
    return '#' + ''.join(['{0:02x}'.format(int(x * 255)) for x in color])


def measure_temp():
    with open('/sys/class/thermal/thermal_zone0/temp') as f:
        temp = f.readline()
        return int(temp) / 1000.0


def doublewrap(f):
    """
        a decorator decorator, allowing the decorator to be used as:
        @decorator(with, arguments, and=kwargs)
        or
        @decorator
    """

    @wraps(f)
    def new_dec(*args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            return f(args[0])
        else:
            return lambda realf: f(realf, *args, **kwargs)

    return new_dec


@doublewrap
def threaded(f, daemon=False):
    """
     a decorator to make a function execute in a new thread.
     a new thread is created and returned from the initial function call.
     the thread object has an attached queue object 'result_queue' that
     receives the result of the function call.

     ie:
         >> @threaded
             def fun( ... ):
                 ...
                 return result

         >> to = fun( ... )  # does not block
         >> to.result_queue
         <Queue.Queue instance at 0x...>
         >> to.result_queue.get()  # blocks
     """

    def wrapped_f(q, *args, **kwargs):
        """
        this function calls the decorated function and puts the
        result in a queue
        """

        ret = f(*args, **kwargs)
        q.put(ret)

    def wrap(*args, **kwargs):
        """
        this is the function returned from the decorator, it fires off
        wrapped_f in a new thread and returns the thread object with
        the result queue attached
        """
        q = queue.Queue()

        t = threading.Thread(target=wrapped_f, args=(q,) + args, kwargs=kwargs)
        t.daemon = daemon
        t.start()
        t.result_queue = q
        return t

    return wrap


@threaded
def set_camera_mode(cam, aem, framerate=None, mode=None):
    cam.exposure_mode = 'auto'
    if mode is not None:
        cam.sensor_mode = mode
    if framerate is not None:
        cam.framerate = framerate

    sleep(3)
    cam.exposure_mode = aem

    print_sensor(cam)


def print_sensor(cam):
    print('Sensor:')
    print(' mode:', cam.sensor_mode)
    print(' framerate:', cam.framerate)
    print(' res:', cam.resolution)
    print(' exposure:', cam.exposure_mode)
    print(' iso:', cam.iso)
