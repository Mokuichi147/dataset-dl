from enum import Enum
from typing import Callable, NoReturn, Optional

from pytube import Stream, YouTube


class NameMode(Enum):
    TITLE = 0
    ID = 1


class Quality:
    def __init__(self,
                text: str,
                is_video: bool,
                is_audio: bool,
                extension_video: str,
                extension_audio: str
            ):
        self.text = text
        self.is_video = is_video
        self.is_audio = is_audio
        self.extension_video = extension_video
        self.extension_audio = extension_audio


class QualityMode(Enum):
    HIGH = Quality(
            text = 'High',
            is_video = True,
            is_audio = True,
            extension_video = 'mp4',
            extension_audio = 'mp4'
        )
    LOW = Quality(
            text = 'Low',
            is_video = True,
            is_audio = True,
            extension_video = 'mp4',
            extension_audio = 'mp4'
        )
    FPS = Quality(
            text = 'High 60fps',
            is_video = True,
            is_audio = True,
            extension_video = 'mp4',
            extension_audio = 'mp4'
        )
    WEBM = Quality(
            text = 'High webm',
            is_video = True,
            is_audio = True,
            extension_video = 'webm',
            extension_audio = 'webm'
        )
    AMP4 = Quality(
            text = 'Audio mp4',
            is_video = False,
            is_audio = True,
            extension_video = '',
            extension_audio = 'mp4'
        )
    OPUS = Quality(
            text = 'Audio opus',
            is_video = False,
            is_audio = True,
            extension_video = '',
            extension_audio = 'opus'
        )
    
    def __init__(self, quality: Quality):
        self._text = quality.text
        self._is_video = quality.is_video
        self._is_audio = quality.is_audio
        self._extension_video = quality.extension_video
        self._extension_audio = quality.extension_audio
    
    @property
    def text(self) -> str:
        return self._text
    
    @property
    def is_video(self) -> bool:
        return self._is_video
    
    @property
    def is_audio(self) -> bool:
        return self._is_audio
    
    @property
    def extension_video(self) -> str:
        return self._extension_video
    
    @property
    def extension_audio(self) -> str:
        return self._extension_audio



def get_qualitymode(text: str) -> Optional[QualityMode]:
    for quality_mode in QualityMode:
        if text == quality_mode.text:
            return quality_mode


def get_request_type(text: str) -> Optional[str]:
    if text == 'mp4':
        return text
    elif text == 'opus' or text == 'webm':
        return 'webm'


def get_video_stream(yt: YouTube, quality_mode: QualityMode) -> Optional[Stream]:
    if not quality_mode.is_video:
        return None
    
    request_type = get_request_type(quality_mode.extension_video)
    stream_query = yt.streams.filter(only_video=True, subtype=request_type)
    
    if quality_mode == QualityMode.LOW:
        return stream_query.order_by('resolution').first()
    
    elif quality_mode == QualityMode.FPS:
        stream = stream_query.filter(fps=60).order_by('resolution').desc().first()
        if stream != None:
            return stream
    
    return stream_query.order_by('resolution').desc().first()


def get_audio_stream(yt: YouTube, quality_mode: QualityMode) -> Optional[Stream]:
    if not quality_mode.is_audio:
        return None
    
    request_type = get_request_type(quality_mode.extension_audio)
    stream_query = yt.streams.filter(only_audio=True, subtype=request_type)
    
    if quality_mode == QualityMode.LOW:
        return stream_query.first()
    
    return stream_query.desc().first()