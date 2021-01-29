# -*- coding: utf-8 -*-
# author: @RShirohara
# TODO: #4, #7


import io
import threading

from pydub import AudioSegment
from pydub.playback import play

from .util import EventQueue


def play_audio(source):
    """Play audio.

    Args:
        source (bytes): Source audio conveted to MP3.
    """

    audio = AudioSegment.from_file(io.BytesIO(source), format='mp3')
    play(audio)


class PlayMP3(threading.Thread):
    """Play MP3 width multithreading.

    Attributes:
        status (Event): Used to indicate if a thread can exec.
        source (EventQueue): Queue to get source audio.
    """

    def __init__(self):
        """Initialise."""
        super(PlayMP3, self).__init__()
        self.status = threading.Event()
        self.source = EventQueue(self.status)

    def run(self):
        """Run thread."""

        while True:
            if not self.status.is_set():
                self.status.wait()
            src = self.source.w_get()
            play_audio(src)
