from pathlib import Path

import picam.config as cfg


class FakeSource(object):
    """
    a fake source of video using previously captured frames
    """

    def __init__(self):
        self._changed = False
        self._index = 0
        self.frame_path = [Path(x) for x in cfg.FAKE_FRAMES_DIR]

    def __iter__(self):
        while True:
            self._changed = False
            for frame in self.frame_path[self._index].iterdir():
                if self._changed:
                    break
                with open(frame, 'rb') as f:
                    buf = f.read()
                yield buf

    def zoom(self):
        self._index = (self._index + 1) % 3
        print('now {}'.format(self.frame_path[self._index]))
        self._changed = True
