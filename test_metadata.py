import sys
from pathlib import Path

from utils.video_utils import get_video_duration
from utils.asr_utils import transcribe_video
from utils.llm_utils import analyze_video
from utils.builder_utils import build_metadata
from utils.face_db_utils import build_face_database
from utils.speaker_utils import assign_speakers



build_face_database("input.mp4")
