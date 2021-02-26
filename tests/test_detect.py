# -*- coding: utf-8 -*-
# tegaki.detect test


import time
from pprint import pprint

from tegaki import detect, util


class TestDetect(detect.DetectArea):
    def __init__(self, model_dir, dev_info, maxsize=0, daemon=None):
        super(detect.DetectArea, self).__init__(
            maxsize=maxsize,
            daemon=daemon
        )
        self.graph, self.sess = detect.load_inference_graph(model_dir)
        self.dev_info = dev_info

    def run(self):
        """Exec."""

        while True:
            if not self.status.is_set():
                self.status.wait()
            source = self.get()

            paper = detect.detect_paper(source, self.dev_info)
            hands = detect.detect_hands(
                source, self.graph, self.sess, self.dev_info
            )
            _result = detect._check_grid(paper, hands)
            pprint({
                'date': time.strftime('%Y-%m-%d %H:%M:%S %Z'),
                'paper': paper,
                'hands': hands,
                'result': _result
            })

        self.sess.close()


if __name__ == "__main__":
    capdev = util.VideoStream().start()
    th_det = TestDetect(
        '/home/y19214/Git/handtracking/hand_inference_graph',
        capdev.info(),
        daemon=True,
    )

    th_det.start()

    while True:
        th_det.put(capdev.read())
        time.sleep(1)
