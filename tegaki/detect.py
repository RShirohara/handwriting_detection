# -*- coding: utf-8 -*-
# author: @RShirohara
# TODO: #1, #2, #3


from threading import Event, Thread
from typing import NamedTuple

import cv2
import numpy as np
import tensorflow as tf

from .util import EventQueue


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


def detect_hands(image_np, detection_graph, sess, thresh=0.7):
    """Hand Detection.
    Generate scores and bounding boxes.

    Args:
        image_np (ndarray): Source image converted to RGB.
        detection_graph (Graph): tf.Graph object.
        sess (Session): tf.Session object.

    Returns:
        tuple[ndarray]: Detected boxes.
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

    result = tuple([
        x
        for x, y in zip(np.squeeze(boxes), np.squeeze(scores))
        if y >= thresh
    ])
    return result


def detect_paper(image_cv, thresh_level=(140, 255), max_area=100000):
    """Paper Detection.
    Generate bounding boxes.

    Args:
        image_cv (ndarray): Source image converted to BGR.
        thresh (tuple[int]): Threshold of the grayscale. (max, min)
        max_area (int): Max area of the paper.
    Returns:
        tuple[ndarray]: Detected boxes.
    """

    image_gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    _, image_gray = cv2.threshold(
        image_gray, thresh_level[0], thresh_level[1], cv2.THRESH_BINARY
    )
    contours = cv2.findContours(
        image_gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )[0]

    boxes = tuple([
        cv2.approxPolyDP(c, 0.1*cv2.arcLength(c, True), True).ravel()
        for c in contours
        if cv2.contourArea(c) >= max_area
    ])

    return boxes


class DetectArea(Thread):
    """Detect paper and hands with multiprocessing.

    Attributes.
        status (Event): Used to indicate if a thread can exec.
        task (EventQueue[ndarray]): Queue to get source image converted to BGR.
        result (EventQueue[ndarray]): Qurue pointer to send results.
    """

    def __init__(self, result, model_dir, dev_info, daemon=None):
        """Initialize.

        Args:
            result (EventQueue[ndarray]): Queue pointer to send results.
            model_dir (str): Path to directory where tensorflow model exists.
            dev_info (CapParams): Capture device infomation.
        """

        super(DetectArea, self).__init__(daemon=daemon)
        self.status = Event()
        self.task = EventQueue(self.status)
        self.result = result
        self.graph, self.sess = load_inference_graph(model_dir)
        self.dev_info = dev_info

    def run(self):
        """Exec."""

        while True:
            if not self.status.is_set():
                self.status.wait()
            source = self.task.w_get()

            paper = detect_paper(source)
            if not paper:
                continue

            hands = detect_hands(source, self.graph, self.sess)
            if not hands:
                continue

            paper_grid = tuple([
                DetectedGrid(
                    min(p[::2]),
                    max(p[::2]),
                    min(p[1::2]),
                    max(p[1::2])
                )
                for p in paper
            ])
            hands_grid = tuple([
                DetectedGrid(
                    int(h[1] * self.dev_info.width),
                    int(h[3] * self.dev_info.width),
                    int(h[0] * self.dev_info.height),
                    int(h[2] * self.dev_info.height)
                )
                for h in hands
            ])

            _result = []
            for pa in paper_grid:
                for ha in hands_grid:
                    _res = []
                    for p, h in zip(pa.get(), ha.get()):
                        if not (
                            p[0] < h[0] < h[1] < p[1] and
                            h[0] < p[0] < p[1] < h[1] and
                            p[0] < h[0] < p[1] < h[1] and
                            h[0] < p[0] < h[1] < p[1]
                        ):
                            _res.append(True)
                        else:
                            _res.append(False)
                    _result.append(tuple(_res))

            if (True, True) in _result:
                self.result.w_put(source)

        self.sess.close()
