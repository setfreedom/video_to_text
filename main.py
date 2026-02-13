import sys
from pathlib import Path

from utils.video_utils import get_video_duration
from utils.asr_utils import transcribe_video
from utils.llm_utils import analyze_video
from utils.builder_utils import build_metadata
from utils.face_db_utils import build_face_database
from utils.speaker_utils import assign_speakers


def main(video_path: str):
    print("\n请选择运行模式：")
    print("1️⃣ 第一次运行（完整流程）")
    print("2️⃣ 第二次运行（跳过耗时步骤）")

    mode = input("请输入 1 或 2：").strip()

    output_path = Path("outputs") / (Path(video_path).stem + "_metadata.json")
    output_path.parent.mkdir(exist_ok=True)

    # =================================================
    # ⭐ 模式1：完整流程
    # =================================================
    if mode == "1":

        print("\n=== STEP 1：获取视频时长 ===")
        duration = get_video_duration(video_path)

        print("\n=== STEP 2：Whisper识别台词 ===")

        dialogues = transcribe_video(video_path)


        print("\n=== STEP 3：建立人物人脸库 ===")
        build_face_database(video_path)


        print("\n=== STEP 5：调用千问分析剧情 ===")
        print(f"台词数量：{len(dialogues)}")
        llm_result = analyze_video(dialogues)
        print("LLM分析完成")

        print("\n=== STEP 6：构建元数据 ===")
        metadata = build_metadata(duration, dialogues, llm_result)

        metadata.save_to_json(output_path)

        print(f"\n✅ 全流程完成：{output_path}")

    # =================================================
    # ⭐ 模式2：快速模式
    # =================================================
    elif mode == "2":

        from video_metadata import VideoMetadata

        if not output_path.exists():
            print("❌ 找不到 metadata，请先运行模式1")
            return

        print("\n=== 加载已有 metadata ===")
        metadata = VideoMetadata.load_from_json(output_path)

        print("\n=== 重新绑定说话人 ===")
        metadata.dialogues = assign_speakers(video_path, metadata.dialogues)

        print("\n=== 重新构建人物列表 ===")
        # 重新生成 people（避免仍然是旧名字）
        metadata.people = []
        seen = set()

        for dlg in metadata.dialogues:
            if dlg.speaker not in seen and dlg.speaker != "未知":
                from video_metadata import Person
                metadata.people.append(Person(dlg.speaker, "未知"))
                seen.add(dlg.speaker)

        metadata.save_to_json(output_path)

        print(f"\n✅ 快速更新完成：{output_path}")

    else:
        print("❌ 输入错误")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python main.py video.mp4")
        sys.exit(1)

    main(sys.argv[1])
