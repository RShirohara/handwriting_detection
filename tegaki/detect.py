# -*- coding: utf-8 -*-
# author: @RShirohara
# TODO: #1, #2, #3


import cv2
import numpy as np
import tensorflow as tf


def load_inference_graph(root):
    """Load a frozen inference graph.

    Args:
        root (str): Path to the directory where the tensorflow model exists.

    Returns:
        detection_graph (Graph): tf.Graph object.
        sess (Session): tf.Session object.
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


def detect_hands(image_np, detection_graph, sess):
    """Hand Detection.
    Generate scores and bounding boxes.

    Args:
        image_np (ndarray): Source image converted to RGB.
        detection_graph (Graph): tf.Graph object.
        sess (Session): tf.Session object.

    Returns:
        boxes (ndarray): Detected boxes.
        scores (ndarray): Detected scores.
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
        'num_detection:0'
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

    return np.squeeze(boxes), np.squeeze(scores)


def detect_paper(image_cv, thresh_level, max_area=100000):
    """Paper Detection.
    Generate bounding boxes.

    Args:
        image_cv (ndarray): Source image converted to BGR.
        thresh_level (tuple[int]): Threshold of the grayscale. (max, min)
        max_area (int): Max area of the paper.
    Returns:
        boxes (tuple): detected boxes
    """

    image_gray = cv2.cvtColor(image_cv, cv.COLOR_BGR2GRAY)
    _, image_gray = cv2.threshold(
        image_gray, thresh_level[0], thresh_level[1], cv2.THRESH_BINARY
    )
    contours = cv2.findContours(
        image_gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )[0]

    boxes = []
    areas = []
    for c in contours:
        area = cv2.contourArea(c)
        epsilon = 0.1 * cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, epsilon, True)
        if len(applox) == 4 and area >= max_area:
            boxes.append(approx)
            areas.append(area)

    boxes.sort(key=lambda x:areas, reverse=True)

    return tuple(boxes)