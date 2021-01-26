# -*- coding: utf-8 -*-
# author: @RShirohara

import cv2
import threading


class VideoStream:
    """Read source input with multithreading.
    This code is based on https://github.com/victordibia/handtracking.

    Attributes:
        stream (VideoCapture): cv2.VideoCapture stream object.
        status (threading.Event): Used to indicate if the thread stopped.
    """

    def __init__(self, src, width, height):
        """Initialize video stream.

        Args:
            src (str): Source URI of video stream.
            width (int): Width of the frames in video stream.
            height (int): Height of the frames in video stream.
        """

        self.stream = cv2.VideoCapture(src)
        self.status = threading.Event()

        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        (self.grabbed, self.frame) = self.stream.read()

        self.status.set()

    def start(self):
        """Start the thread to read frames from cv2 stream."""

        threading.Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while True:
            if not self.status.is_set():
                return
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        """Return frame most recentry read."""
        return self.frame

    def size(self):
        """Return size of the capture device.

        Returns:
            (int, int): width, height
        """

        return self.stream.get(3), self.stream.read(4)

    def stop(self):
        self.status.wait()
