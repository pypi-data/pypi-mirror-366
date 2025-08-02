# Copyright 2025 DeepMind Technologies Limited. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""MIME types commonly used by Processors at the `Part` level.

Processors uses MIME types to express part modalities[^1].

If this file doesn't contain an appropriate MIME type you can pick one from
https://www.iana.org/assignments/media-types/media-types.xhtml
or define a custom */x-*.
"""

from typing import Any

IMAGE_PNG = 'image/png'
IMAGE_JPEG = 'image/jpeg'
IMAGE_WEBP = 'image/webp'
IMAGE_HEIC = 'image/heic'
IMAGE_HEIF = 'image/heif'


INPUT_IMAGE_TYPES = [
    IMAGE_HEIF,
    IMAGE_HEIC,
    IMAGE_JPEG,
    IMAGE_PNG,
    IMAGE_WEBP,
]

AUDIO_AAC = 'audio/aac'
AUDIO_FLAC = 'audio/flac'
AUDIO_MP3 = 'audio/mp3'
AUDIO_M4A = 'audio/m4a'
AUDIO_MPEG = 'audio/mpeg'
AUDIO_MPGA = 'audio/mpga'
AUDIO_MP4 = 'audio/mp4'
AUDIO_OPUS = 'audio/opus'
AUDIO_PCM = 'audio/pcm'
AUDIO_WAV = 'audio/wav'
AUDIO_WEBM = 'audio/webm'

INPUT_AUDIO_TYPES = [
    AUDIO_AAC,
    AUDIO_FLAC,
    AUDIO_MP3,
    AUDIO_M4A,
    AUDIO_MPEG,
    AUDIO_MPGA,
    AUDIO_MP4,
    AUDIO_OPUS,
    AUDIO_PCM,
    AUDIO_WAV,
    AUDIO_WEBM,
]


VIDEO_MOV = 'video/mov'
VIDEO_MPEG = 'video/mpeg'
VIDEO_MPEGPS = 'video/mpegps'
VIDEO_MPG = 'video/mpg'
VIDEO_MP4 = 'video/mp4'
VIDEO_WEBM = 'video/webm'
VIDEO_WMV = 'video/wmv'
VIDEO_X_FLV = 'video/x-flv'
VIDEO_3GPP = 'video/3gpp'
VIDEO_QUICKTIME = 'video/quicktime'

INPUT_VIDEO_TYPES = [
    VIDEO_MOV,
    VIDEO_MPEG,
    VIDEO_MPEGPS,
    VIDEO_MPG,
    VIDEO_MP4,
    VIDEO_WEBM,
    VIDEO_WMV,
    VIDEO_X_FLV,
    VIDEO_3GPP,
    VIDEO_QUICKTIME,
]

TEXT_PDF = 'application/pdf'
TEXT_PLAIN = 'text/plain'
TEXT_CSV = 'text/csv'
TEXT_HTML = 'text/html'
TEXT_XML = 'text/xml'
TEXT_PYTHON = 'text/x-python'
TEXT_SCRIPT_PYTHON = 'text/x-script.python'
TEXT_JSON = 'application/json'
TEXT_ENUM = 'text/x.enum'

INPUT_TEXT_TYPES = [
    TEXT_PLAIN,
    TEXT_CSV,
    TEXT_HTML,
    TEXT_XML,
    TEXT_PYTHON,
    TEXT_SCRIPT_PYTHON,
    TEXT_JSON,
]

ALL_SUPPORTED_INPUT_TYPES = (
    INPUT_IMAGE_TYPES + INPUT_AUDIO_TYPES + INPUT_VIDEO_TYPES + INPUT_TEXT_TYPES
)

TEXT_EXCEPTION = 'text/x-exception'


def is_text(mime: str) -> bool:
  """Returns whether the content is a human-readable text."""
  return (
      mime in INPUT_TEXT_TYPES
      or mime.startswith('text/')
      or mime.startswith(TEXT_JSON)
  )


def is_json(mime: str) -> bool:
  """Returns whether the content is a human-readable json."""
  return mime.startswith(TEXT_JSON)


def is_dataclass(mime: str, json_dataclass: type[Any] | None = None) -> bool:
  """Returns whether the content is a dataclass."""
  type_name = json_dataclass.__name__ if json_dataclass else ''
  return mime.startswith(f'application/json; type={type_name}')


def is_image(mime: str) -> bool:
  """Returns whether the content is an image."""
  return (mime in INPUT_IMAGE_TYPES) or mime.startswith('image/')


def is_video(mime: str) -> bool:
  """Returns whether the content is a video.

  Args:
    mime: The mime string.

  Returns:
    True of it is a video, False otherwise.
  """
  return (mime in INPUT_VIDEO_TYPES) or mime.startswith('video/')


def is_audio(mime: str) -> bool:
  """Returns whether the content is audio."""
  return (mime in INPUT_AUDIO_TYPES) or mime.startswith('audio/')


def is_streaming_audio(mime: str) -> bool:
  """Returns whether the content is streaming audio."""
  return mime.startswith('audio/l16')


def is_wav(mime: str) -> bool:
  """Returns whether the content is a wav file."""
  return mime == AUDIO_WAV


def is_source_code(mime: str) -> bool:
  """Returns whether the content is a source code in some language."""
  # This list is incomplete and will be extended on as-needed basis.
  return mime in (
      'text/x-python',
      'application/x-latex',
      'text/x-c',
  )


def is_pdf(mime: str) -> bool:
  """Returns whether the content is a PDF."""
  return mime == TEXT_PDF


def is_csv(mime: str) -> bool:
  """Returns whether the content is a CSV file."""
  return mime == TEXT_CSV


def is_python(mime: str) -> bool:
  """Returns whether the content is python code."""
  return mime in [TEXT_PYTHON, TEXT_SCRIPT_PYTHON]


def is_exception(mime: str) -> bool:
  """Returns whether the content is an exception."""
  return mime == TEXT_EXCEPTION
