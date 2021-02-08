# -*- coding: utf-8 -*-
# author: @RShirohara


from threading import Event, Thread
from typing import NamedTuple

import cv2
from google.cloud import texttospeech, vision

from .util import EventQueue


class DetectedText(NamedTuple):
    text: str
    lang: str = "ja_JP"


class GoogleOCR:
    """Google Cloud Vision OCR api wrapper.

    Attributes:
        client (ImageAnnotatorClient): GCV api ImageAnnotator service client.
    """

    def __init__(self):
        self.client = vision.ImageAnnotatorClient()

    def get(self, source):
        """Detect handwriting text.

        Args:
            source (bytes): Source image converterd to PNG or JPEG format.

        Returns:
            text_annotations (RepeatedComposite): responce.text_annotations
        """

        image = vision.Image(content=source)
        responce = self.client.document_text_detection(image=image)

        return responce.full_text_annotation


class GoogleTTS:
    """Google Cloud Text-to-Speech api wrapper.

    Attributes:
        client (TextToSpeechClient): TTS service client.
    """

    def __init__(self):
        self.client = texttospeech.TextToSpeechClient()

    def get(self, source, lang="ja_JP"):
        """Synthesizes speech from input string.

        Args:
            source (str): Source text.
            lang (str): Language code formatted to locale.
                        example: ja_JP

        Returns:
            audio (bytes): audio_content converted to mp3 format.
        """

        synthesis_input = texttospeech.SynthesisInput(text=source)
        voice = texttospeech.VoiceSelectionParams(
            language_code=lang,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        responce = self.client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        return responce.audio_content


class DetectText(Thread):
    """Detect text with multithreading.

    Attributes:
        api (GoogleOCR): Google Cloud Vision api.
        stauts (Event): used to indicate if a thread can exec.
        task (EventQueue[ndarray]): Queue to get source image converted to BGR.
        result (EventQueue[DetectedText]): Queue pointer to send results.
    """

    def __init__(self, result, maxsize=0, daemon=None):
        """Initialize.

        Args:
            result (EventQueue[DetectedText]): Queue pointer to send results.
            maxsize (int): Upperbound limit on the item in the queue.
        """

        super(DetectText, self).__init__(daemon=daemon)
        self.api = GoogleOCR()
        self.status = Event()
        self.task = EventQueue(self.status, maxsize=maxsize)
        self.result = result

    def run(self):
        """Run thread."""

        _before = []
        _para = []

        while True:
            if not self.status.is_set():
                self.status.wait()
            task = self.task.w_get()
            res = self.api.get(cv2.imencode('.jpg', task)[1].tobytes())

            for page in res.pages:
                for block in page.blocks:
                    for para in block.paragraphs:
                        _para.append([
                            ''.join([s.text for s in w.symbols])
                            for w in para.words
                            if para.confidence >= 0.85
                        ])

            for p in _para:
                if not set(p) in _before:
                    self.result.w_put(DetectedText(''.join(p)))
                    _before.append(set(p))


class GetTTS(Thread):
    """Get Syntheshis speech with multithreading.

    Attributes:
        api (GoogleTTS): Google Text-to-Speech api.
        status (Event): Used to indicate if a thread can exec.
        task (EventQueue[DetectedText]): Queue to get source text.
        result (EventQueue): Queue pointer to send results.
    """

    def __init__(self, result, maxsize=0, daemon=None):
        """Initialize.

        Args:
            result (EventQueue): Queue pointer to send results.
            maxsize (int): Upperbound limit on the item in the queue.
        """

        super(GetTTS, self).__init__(daemon=daemon)
        self.api = GoogleTTS()
        self.status = Event()
        self.task = EventQueue(self.status, maxsize=maxsize)
        self.result = result

    def run(self):
        """Run thread."""

        while True:
            if not self.status.is_set():
                self.status.wait()
            task = self.task.w_get()
            res = self.api.get(task.text, lang=task.lang)
            self.result.w_put(res)
