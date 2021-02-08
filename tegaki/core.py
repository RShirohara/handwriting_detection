# -*- coding: utf-8 -*-
# author: @RShirohara
# TODO: #8


import time

from .detect import DetectArea
from .googleapis import DetectText, GetTTS
from .send import PlayMP3
from .util import VideoStream


class Tegaki:
    """HandWriting Detection core class.

    Attributes:
        capture (VideoStream): Video stream from source device or file.
        cap_params (CapParams): infomation of source device or file.
    """

    def __init__(self, model_dir, src=0, width=None, height=None, maxsize=0):
        """Initilize core class.

        Args:
            model_dir (str): Path to protocol buffer (.pb) file.
            src (str, int): Path to capture device or file.
            width (int): Width of the frames in stream.
            height (int): Height of the frames in stream.
            maxsize (int): Upperbound limit on the item in the queue.
        """

        self.capture = VideoStream(
            src=src, width=width, height=height
        ).start()
        self.cap_params = self.capture.info()

        self.th_play = PlayMP3(daemon=True, maxsize=maxsize)
        self.th_tts = GetTTS(self.th_play.task, daemon=True, maxsize=maxsize)
        self.th_ocr = DetectText(
            self.th_tts.task,
            daemon=True,
            maxsize=maxsize
        )
        self.th_det = DetectArea(
            self.th_ocr.task,
            model_dir,
            self.cap_params,
            daemon=True,
            maxsize=maxsize
        )

    def run(self):
        """Exec."""

        self.th_play.start()
        self.th_tts.start()
        self.th_ocr.start()
        self.th_det.start()

        while True:
            self.th_det.task.w_put(self.capture.read())
            if self.th_tts.status.is_set():
                time.sleep(10)
