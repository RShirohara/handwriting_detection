# -*- coding: utf-8 -*-
# author: @RShirohara


from typing import NamedTuple

import cv2
import numpy as np
import tensorflow as tf

from .util import EventThread


class DetectedGrid(NamedTuple):
    """Detected object coordinate."""

    xmin: int
    xmax: int
    ymin: int
    ymax: int

    def get(self):
        return (self.xmin, self.xmax), (self.ymin, self.ymax)


def load_inference_graph(root):
    """Load a frozen inference graph.

    Args:
        root (str): Path to the directory where the tensorflow model exists.

    Returns:
        Graph: tf.Graph object.
        Session: tf.Session object.
    """

    ckpt_path = root + '/frozen_inference_graph.pb'
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.compat.v1.GraphDef()
        with tf.io.gfile.GFile(ckpt_path, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')
        sess = tf.Session(graph=detection_graph)
    return detection_graph, sess


def detect_hands(image_np, detection_graph, sess, dev_info, thresh=0.7):
    """Hand Detection.
    Generate scores and bounding boxes.

    Args:
        image_np (ndarray): Source image converted to RGB.
        detection_graph (Graph): tf.Graph object.
        sess (Session): tf.Session object.
        dev_info (CapParams): Capture device infomation.

    Returns:
        tuple[DetectedGrid]: Detected boxes.
    """

    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
    detection_boxes = detection_graph.get_tensor_by_name(
        'detection_boxes:0'
    )
    detection_scores = detection_graph.get_tensor_by_name(
        'detection_scores:0'
    )
    detection_classes = detection_graph.get_tensor_by_name(
        'detection_classes:0'
    )
    num_detections = detection_graph.get_tensor_by_name(
        'num_detections:0'
    )

    image_np_expanded = np.expand_dims(image_np, axis=0)

    boxes, scores, classes, num = sess.run(
        [
            detection_boxes,
            detection_scores,
            detection_classes,
            num_detections
        ],
        feed_dict={image_tensor: image_np_expanded}
    )

    _raw_grids = (
        x
        for x, y in zip(np.squeeze(boxes), np.squeeze(scores))
        if y >= thresh
    )

    return tuple(
        DetectedGrid(
            int(_r[1] * dev_info.width),
            int(_r[3] * dev_info.width),
            int(_r[0] * dev_info.height),
            int(_r[2] * dev_info.height)
        )
        for _r in _raw_grids
        if _raw_grids
    )


def detect_paper(image_cv, dev_info, thresh_level=(140, 255), max_area=100000):
    """Paper Detection.
    Generate bounding boxes.

    Args:
        image_cv (ndarray): Source image converted to BGR.
        dev_info (CapParams): Capture device infomation.
        thresh_level (tuple[int]): Threshold of the grayscale. (max, min)
        max_area (int): Max area of the paper.

    Returns:
        tuple[DetectedGrid]: Detected boxes.
    """

    _thresh_grid = (dev_info.width / 10, dev_info.height / 10)

    image_gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    _, image_gray = cv2.threshold(
        image_gray, thresh_level[0], thresh_level[1], cv2.THRESH_BINARY
    )
    contours = cv2.findContours(
        image_gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )[0]

    _raw_grids = tuple(
        cv2.approxPolyDP(c, 0.1*cv2.arcLength(c, True), True).ravel()
        for c in contours
        if cv2.contourArea(c) >= max_area
    )

    _result = (
        DetectedGrid(
            min(_r[::2]),
            max(_r[::2]),
            min(_r[1::2]),
            max(_r[1::2])
        )
        for _r in _raw_grids
        if _raw_grids
    )

    return tuple(
        _r
        for _r in _result
        if (
            _r.xmin > _thresh_grid[0] and
            _r.xmax < (dev_info.width - _thresh_grid[0]) and
            _r.ymin > _thresh_grid[1] and
            _r.ymax < (dev_info.height - _thresh_grid[1])
        )
    )


def _check_grid(paper, hands):
    """Check grids.

    Args:
        paper (iter[DetectedGrid]): Papers grid.
        hands (iter[DetectedGrid]): Hands grid.
    Returns:
        tuple[tuple[bool]]: Results.
    """

    _results = tuple(
        tuple(
            True
            if not (
                _p[0] < _h[0] < _h[1] < _p[1] or
                _h[0] < _p[0] < _p[1] < _h[1] or
                _p[0] < _h[0] < _p[1] < _h[1] or
                _h[0] < _p[0] < _h[1] < _p[1]
            )
            else False
            for _p, _h in zip(_pa.get(), _ha.get())
        )
        for _ha in hands
        for _pa in paper
    )
    return _results


class DetectArea(EventThread):
    """Detect paper and hands with multiprocessing.

    Attributes.
        status (bool): Used to indicate if a thread can exec.
        result (Queue[ndarray]): Pointer used to send results.
    """

    def __init__(self, result, model_dir, dev_info, maxsize=0, daemon=None):
        """Initialize.

        Args:
            result (Queue[ndarray]): Queue pointer to send results.
            model_dir (str): Path to directory where tensorflow model exists.
            dev_info (CapParams): Capture device infomation.
            maxsize (int): Upper bound limit on the item in the queue.
        """

        super(DetectArea, self).__init__(
            result=result,
            maxsize=maxsize,
            daemon=daemon
        )
        self.graph, self.sess = load_inference_graph(model_dir)
        self.dev_info = dev_info

    def run(self):
        """Exec."""

        while True:
            if not self.status.is_set():
                self.status.wait()
            source = self.get()

            _result = _check_grid(
                detect_paper(source, self.dev_info),
                detect_hands(source, self.graph, self.sess, self.dev_info)
            )

            if (False, False) not in _result:
                self.result.put(source)

        self.sess.close()
