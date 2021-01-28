# -*- coding: utf-8 -*-
# author: @RShirohara
# TODO: #4, #7


import io
import threading

from pydub import AudioSegment
from pydub.playback import play


def play_audio(source):
    """Play audio.

    Args:
        source (bytes): Source audio conveted to MP3.
    """

    audio = AudioSegment.from_file(io.BytesIO(source), format='mp3')
    play(audio)


class PlayMP3(threading.Thread):
    """Play MP3 width multithreading."""
    pass
