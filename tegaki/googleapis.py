# -*- coding: utf-8 -*-
# author: @RShirohara
# TODO: #4, #7


import threading
from typing import NamedTuple

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

        return responce.text_annotations


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


class DetectText(threading.Thread):
    """Detect text with multithreading.

    Attributes:
        api (GoogleOCR): Google Cloud Vision api.
    """
    pass


class GetTTS(threading.Thread):
    """Get Syntheshis speech with multithreading.

    Attributes:
        api (GoogleTTS): Google Text-to-Speech api.
        status (Event): Used to indicate if a thread can exec.
        source (EventQueue): Queue to get source text.
        result (EventQueue): Queue pointer to send results.
    """

    def __init__(self, result):
        """Initialize.

        Args:
            result (EventQueue): Queue pointer to send results.
        """

        super(GetTTS, self).__init__()
        self.api = GoogleTTS()
        self.status = threading.Event()
        self.source = EventQueue(self.status)
        self.result = result

    def run(self):
        """Run thread."""

        while True:
            if not self.status.is_set():
                self.status.wait()
            task = self.source.w_get()
            res = self.api.get(task.text, lang=task.lang)
            self.result.w_put(res)
