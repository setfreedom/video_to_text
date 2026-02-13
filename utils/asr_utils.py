import subprocess
from pathlib import Path

from faster_whisper import WhisperModel
from video_metadata import Dialogue


MODEL_PATH = r"D:\python\models\models\faster-whisper-medium"


def extract_audio(video_path: str) -> str:
    """
    使用 ffmpeg 提取 wav 音频
    """
    audio_path = Path("outputs") / (Path(video_path).stem + ".wav")
    audio_path.parent.mkdir(exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-ac", "1",          # 单声道
        "-ar", "16000",      # 采样率16k
        "-vn",               # 不要视频
        str(audio_path)
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return str(audio_path)


def transcribe_video(video_path: str):
    """
    稳定版 ASR：
    1. 先提取音频
    2. 再进行识别
    """

    print("🎧 提取音频...")
    audio_path = extract_audio(video_path)

    print("🧠 加载 Whisper 模型...")
    model = WhisperModel(
        MODEL_PATH,
        device="cuda",
        compute_type="int8"
    )

    print("🎙 开始语音识别...")

    segments, _ = model.transcribe(
        audio_path,
        language="zh",
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=2000),
    )

    dialogues = []

    for i, seg in enumerate(segments):
        print(f"识别 {i+1}: {seg.start:.1f}s → {seg.end:.1f}s")

        dlg = Dialogue(
            start_time=seg.start,
            end_time=seg.end,
            speaker="未知",
            text=seg.text.strip()
        )

        dialogues.append(dlg)

    print(f"✅ 共识别 {len(dialogues)} 条台词")

    return dialogues
