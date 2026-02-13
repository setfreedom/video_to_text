from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


def analyze_video(dialogues):
    text = "\n".join([d.text for d in dialogues[:200]])

    prompt = f"""
你是视频理解专家，请分析以下视频台词并返回JSON：

台词：
{text}

返回格式：
{{
 "video_type": "",
 "core_theme": "",
 "people": [
    {{"name": "", "identity": ""}}
 ]
}}
"""

    resp = client.chat.completions.create(
        model="qwen-plus",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    import json
    return json.loads(resp.choices[0].message.content)
