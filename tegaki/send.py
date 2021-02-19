# -*- coding: utf-8 -*-
# author: @RShirohara
# TODO: #7


import io
from threading import Event, Thread

from pydub import AudioSegment
from pydub.playback import play

from .util import EventQueue


def play_audio(source):
    """Play audio.

    Args:
        source (bytes): Source audio conveted to MP3.
    """

    if not source:
        return
    audio = AudioSegment.from_file(io.BytesIO(source), format='mp3')
    play(audio)


class PlayMP3(Thread):
    """Play MP3 width multithreading.

    Attributes:
        status (Event): Used to indicate if a thread can exec.
        task (EventQueue): Queue to get source audio.
    """

    def __init__(self, maxsize=0, daemon=None):
        """Initialize.

        Args:
            maxsize (int): Upperbound limit on the item in the queue.
        """

        super(PlayMP3, self).__init__(daemon=daemon)
        self.status = Event()
        self.task = EventQueue(self.status, maxsize=maxsize)

    def run(self):
        """Run thread."""

        while True:
            if not self.status.is_set():
                self.status.wait()
            src = self.task.w_get()
            if src:
                play_audio(src)
