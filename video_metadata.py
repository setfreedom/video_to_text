# video_metadata.py
import json
from dataclasses import dataclass, asdict
from typing import List, Optional
from pathlib import Path

def _validate_non_empty(s: str, field_name: str):
    if not s or not s.strip():
        raise ValueError(f"{field_name} 不能为空或仅包含空白字符")

def _validate_time_range(start: float, end: float, label: str):
    if start < 0 or end < 0:
        raise ValueError(f"{label} 时间不能为负数")
    if start >= end:
        raise ValueError(f"{label} 起始时间必须小于结束时间")

@dataclass
class BasicInfo:
    duration_seconds: float      # 视频总时长（秒），必须 > 0
    video_type: str              # 如 "剧情片", "纪录片", "广告"
    core_theme: str              # 一句话概括核心主题

    def __post_init__(self):
        if self.duration_seconds <= 0:
            raise ValueError("duration_seconds 必须大于 0")
        _validate_non_empty(self.video_type, "video_type")
        _validate_non_empty(self.core_theme, "core_theme")

@dataclass
class Shot:
    start_time: float            # 起始时间（秒）
    end_time: float              # 结束时间（秒）
    description: str             # 核心画面/动作描述，直白简洁

    def __post_init__(self):
        _validate_time_range(self.start_time, self.end_time, "Shot")
        _validate_non_empty(self.description, "Shot.description")

@dataclass
class Person:
    name: str                    # 姓名；若未知建议写 "未知"
    identity: str                # 身份/角色

    def __post_init__(self):
        _validate_non_empty(self.name, "Person.name")
        _validate_non_empty(self.identity, "Person.identity")

@dataclass
class Dialogue:
    start_time: float            # 台词开始时间（秒）
    end_time: float              # 台词结束时间（秒）
    speaker: str                 # 发言人姓名；无法识别时写 "未知"
    text: str                    # 原文台词，不得修改

    def __post_init__(self):
        _validate_time_range(self.start_time, self.end_time, "Dialogue")
        _validate_non_empty(self.speaker, "Dialogue.speaker")
        _validate_non_empty(self.text, "Dialogue.text")

@dataclass
class VideoMetadata:
    basic_info: BasicInfo
    shots: List[Shot]
    people: List[Person]
    dialogues: List[Dialogue]

    def __post_init__(self):
        # 可选：验证时间是否在视频总时长内（按需启用）
        dur = self.basic_info.duration_seconds
        for shot in self.shots:
            if shot.end_time > dur + 1.0:  # 允许 1 秒误差
                raise ValueError(f"Shot 超出视频总时长: {shot}")
        for dlg in self.dialogues:
            if dlg.end_time > dur + 1.0:
                raise ValueError(f"Dialogue 超出视频总时长: {dlg}")

    def to_dict(self) -> dict:
        """转换为可 JSON 序列化的字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "VideoMetadata":
        """从字典重建对象，对格式错误提供清晰提示"""
        try:
            # 验证顶层字段存在
            required_top_fields = {"basic_info", "shots", "people", "dialogues"}
            missing_top = required_top_fields - data.keys()
            if missing_top:
                raise ValueError(f"缺少顶层字段: {missing_top}")

            basic_data = data["basic_info"]
            required_basic = {"duration_seconds", "video_type", "core_theme"}
            missing_basic = required_basic - basic_data.keys()
            if missing_basic:
                raise ValueError(f"basic_info 缺少字段: {missing_basic}")

            # 尝试构建对象
            basic = BasicInfo(**basic_data)
            shots = [Shot(**s) for s in data["shots"]]
            people = [Person(**p) for p in data["people"]]
            dialogues = [Dialogue(**d) for d in data["dialogues"]]
            return cls(basic_info=basic, shots=shots, people=people, dialogues=dialogues)

        except (TypeError, ValueError, KeyError) as e:
            # 捕获所有可能的数据错误，统一转为 ValueError
            raise ValueError(f"无效的 VideoMetadata 数据结构: {e}") from None

    def save_to_json(self, filepath: str | Path):
        """保存到 JSON 文件"""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load_from_json(cls, filepath: str | Path) -> "VideoMetadata":
        """从 JSON 文件加载"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    # 辅助方法（可选）
    def get_duration_formatted(self) -> str:
        secs = int(self.basic_info.duration_seconds)
        h, m, s = secs // 3600, (secs % 3600) // 60, secs % 60
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        else:
            return f"{m:02d}:{s:02d}"