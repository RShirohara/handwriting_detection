# -*- coding: utf-8 -*-
# author: @RShirohara
# TODO: #7


import io

from pydub import AudioSegment
from pydub.playback import play

from .util import EventThread


def play_audio(source):
    """Play audio.

    Args:
        source (bytes): Source audio conveted to MP3.
    """

    if not source:
        return
    audio = AudioSegment.from_file(io.BytesIO(source), format='mp3')
    play(audio)


class PlayMP3(EventThread):
    """Play MP3 with multithreading.

    Attributes:
        status (Event): Used to indicate if a thread can exec.
    """

    def __init__(self, maxsize=0, daemon=None):
        """Initialize.

        Args:
            maxsize (int): Upperbound limit on the item in the queue.
        """

        super(PlayMP3, self).__init__(
            maxsize=maxsize,
            daemon=daemon
        )

    def run(self):
        """Run thread."""

        while True:
            if not self.status.is_set():
                self.status.wait()
            src = self.get()
            if src:
                play_audio(src)
