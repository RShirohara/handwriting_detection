# -*- coding: utf-8 -*-
# author: @RShirohara


from queue import Queue, Empty
from threading import Event, Thread
from typing import NamedTuple

import cv2


class CapParams(NamedTuple):
    """Capture device params."""
    source: str
    width: int
    height: int


class EventThread(Thread):
    """threading.Thread wrapper.

    Attributes:
        status (Event): Used to indicate if a thread can exec.
        result (EventThread): Pointer used to send results.

        _task (Queue): Used to get tasks.
                       Hidden for consistency with self.status.
                       You must use self.get and self.put for access.
    """

    def __init__(self, result=None, maxsize=0, daemon=None):
        """Initialize.

        Args:
            result (EventThread): Pointer used to send results.
            maxsize (int): Upperbound limit on the item in the Queue.
            daemon (bool): Used to set daemonize.
        """

        super(EventThread, self).__init__(daemon=daemon)
        self._task = Queue(maxsize=maxsize)
        self.status = Event()

        if result:
            self.result = result

    def get(self, block=True, timeout=None):
        """Queue.get wrapper."""

        get = self._task.get(block=block, timeout=timeout)
        if self._task.empty():
            self.status.clear()
        return get

    def put(self, item, block=True, timeout=None):
        """Queue.put wrapper."""

        if self._task.empty():
            self.status.set()
        self._task.put(item, block=block, timeout=timeout)

    def run(self):
        """Run thread."""

        pass


class QueueSplitter:
    """Queue splitter.

    Attribures:
        target (list[Queue]): Target queues.
    """

    def __init__(self, target):
        """Initialize.

        Args:
            target (list[Queue]): Target queues.
        """

        self.target = target

    def qsize(self):
        """Queue.qsize wrapper."""
        return tuple(
            [t.qsize() for t in self.target]
        )

    def empty(self):
        """Queue.empty wrapper."""
        return tuple(
            [t.empty() for t in self.target]
        )

    def full(self):
        """Queue.full wrapper."""
        return tuple(
            [t.full() for t in self.target]
        )

    def put(self, item, block=True, timeout=None):
        """Queue.put wrapper."""
        for t in self.target:
            t.put(item, block=block, timeout=timeout)

    def get(self, block=True, timeout=None):
        """Queue.get wrapper."""
        _res = []
        for t in self.target:
            try:
                _r = t.get(block=block, timeout=timeout)
            except Empty:
                _r = None
            _res.append(_r)
        return tuple(_res)


class VideoStream:
    """Reading source with multithreading.
    This code is based on https://github.com/victordibia/handtracking.

    Attributes:
        source (str): Device name.
        stream (VideoCapture): cv2.VideoCapture stream object.
        status (Event): Used to indicate if the thread stopped.
    """

    def __init__(self, src=0, width=None, height=None):
        """Initialize video stream.

        Args:
            src (str, int): Source URI of the video stream.
            width (int): Width of the frames in the video stream.
            height (int): Height of the frames in the video stream.
        """

        self.source = str(src)
        self.stream = cv2.VideoCapture(src)
        self.status = Event()

        if width and height:
            self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        (self.grabbed, self.frame) = self.stream.read()
        self.status.set()

    def start(self):
        """Start the thread to read frames from cv2 stream."""

        Thread(target=self.update, args=(), daemon=True).start()
        return self

    def update(self):
        while True:
            if not self.status.is_set():
                return
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        """Return frame most recentry read."""
        return self.frame

    def info(self):
        """Return info of the capture device.

        Returns:
            CapParams: Device name, width, and height.
        """

        return CapParams(self.source, self.stream.get(3), self.stream.get(4))

    def stop(self):
        self.status.clear()
