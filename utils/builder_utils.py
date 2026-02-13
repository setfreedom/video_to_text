from video_metadata import (
    BasicInfo, Shot, Person, VideoMetadata
)


def build_metadata(duration, dialogues, llm_result):
    # BasicInfo
    basic = BasicInfo(
        duration_seconds=duration,
        video_type=llm_result["video_type"],
        core_theme=llm_result["core_theme"]
    )

    # Shots（每句台词一个镜头）
    shots = []
    for dlg in dialogues:
        shots.append(
            Shot(
                start_time=dlg.start_time,
                end_time=dlg.end_time,
                description=dlg.text[:30]
            )
        )

    # People
    people = []
    for p in llm_result["people"]:
        people.append(Person(p["name"], p["identity"]))

    metadata = VideoMetadata(
        basic_info=basic,
        shots=shots,
        people=people,
        dialogues=dialogues
    )

    return metadata
