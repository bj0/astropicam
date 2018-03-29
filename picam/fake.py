from pathlib import Path

import picam.config as cfg


class FakeSource(object):
    """
    a fake source of video using previously captured frames
    """
    frame_path = Path(cfg.FAKE_FRAMES_DIR)

    def __iter__(self):
        while True:
            for frame in self.frame_path.iterdir():
                with open(frame, 'rb') as f:
                    buf = f.read()
                yield buf

