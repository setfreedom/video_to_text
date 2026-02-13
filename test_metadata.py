from pathlib import Path
from video_metadata import VideoMetadata


def test_metadata(json_path: str):
    print("🔍 开始测试元数据文件...")

    path = Path(json_path)

    if not path.exists():
        print("❌ 文件不存在:", json_path)
        return

    try:
        # 1️⃣ 加载 JSON 并验证结构
        metadata = VideoMetadata.load_from_json(path)

        print("✅ JSON结构合法")

        # 2️⃣ 打印基础信息
        basic = metadata.basic_info
        print("\n📌 基础信息")
        print("时长:", metadata.get_duration_formatted())
        print("类型:", basic.video_type)
        print("主题:", basic.core_theme)

        # 3️⃣ 统计信息
        print("\n📊 统计")
        print("镜头数量:", len(metadata.shots))
        print("人物数量:", len(metadata.people))
        print("台词数量:", len(metadata.dialogues))

        # 4️⃣ 随机显示几个样本
        print("\n🎬 示例镜头:")
        for shot in metadata.shots[:3]:
            print(f"  {shot.start_time:.2f}-{shot.end_time:.2f}: {shot.description}")

        print("\n💬 示例台词:")
        for dlg in metadata.dialogues[:3]:
            print(f"  {dlg.start_time:.2f}-{dlg.end_time:.2f}: {dlg.text}")

        print("\n👤 人物列表:")
        for p in metadata.people:
            print(f"  {p.name} - {p.identity}")

        print("\n🎉 测试通过：元数据完全合法！")

    except Exception as e:
        print("\n❌ 测试失败")
        print("错误原因:", str(e))


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python test_metadata.py metadata.json")
        sys.exit(1)

    test_metadata(sys.argv[1])
