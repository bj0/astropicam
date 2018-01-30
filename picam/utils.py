import re


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
