# -*- coding: utf-8 -*-
# author: @RShirohara


from multiprocessing import get_context
from multiprocessing.queues import Queue
from threading import Event, Thread
from typing import NamedTuple, Union

import cv2


class CapParams(NamedTuple):
    """Capture device params."""
    source: Union[int, str]
    width: int
    height: int


class EventQueue(Queue):
    """Queue wrapper.

    Attributes:
        status (Event): Used to indicate if a target process is executable.
    """

    def __init__(self, flag, maxsize=0):
        """Initialize.

        Args:
            flag (Event): target Event.
        """

        super(EventQueue, self).__init__(ctx=get_context(), maxsize=maxsize)
        self._status = flag

    def w_get(self, block=True, timeout=None):
        """queue.get wrapper."""

        get = self.get(block=block, timeout=timeout)
        if self.empty():
            self._status.clear()
        return get

    def w_put(self, item, block=True, timeout=None):
        """queue.put wrapper."""

        if self.empty():
            self._status.set()
        return self.put(item, block=block, timeout=timeout)


class VideoStream:
    """Reading source with multithreading.
    This code is based on https://github.com/victordibia/handtracking.

    Attributes:
        stream (VideoCapture): cv2.VideoCapture stream object.
        status (threading.Event): Used to indicate if the thread stopped.
    """

    def __init__(self, src=0, width=640, height=320):
        """Initialize video stream.

        Args:
            src (str, int): Source URI of the video stream.
            width (int): Width of the frames in the video stream.
            height (int): Height of the frames in the video stream.
        """

        self.stream = cv2.VideoCapture(src)
        self.status = Event()

        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        (self.grabbed, self.frame) = self.stream.read()

        self.status.set()

    def start(self):
        """Start the thread to read frames from cv2 stream."""

        Thread(target=self.update, args=()).start()
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
        self.status.clear()
