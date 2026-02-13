import os
import json
from flask import Flask, request, redirect,send_from_directory

OUTPUT_DIR = "outputs"
DB_PATH = os.path.join(OUTPUT_DIR, "face_db.json")

app = Flask(__name__)


def load_db():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(db):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


@app.route("/", methods=["GET", "POST"])
def index():
    db = load_db()

    if request.method == "POST":
        for pid in db:
            db[pid]["name"] = request.form.get(f"name_{pid}", db[pid]["name"])
        save_db(db)
        return redirect("/")

    html = "<h1>人物校正</h1><form method='post'>"

    for pid, person in db.items():

        img_path =  person["image"]
        
        html += f"""
        <div style='margin:20px'>
            <img src='/image/{img_path}' width='120'><br>
            <input name='name_{pid}' value='{person["name"]}' style='width:200px'>
        </div>
        """

    html += "<button type='submit'>保存</button></form>"
    return html


@app.route("/image/<path:filename>")
def serve_image(filename):
    return send_from_directory("outputs", filename)


if __name__ == "__main__":
    # 关键：让 Flask 能访问 outputs 目录
    app.static_folder = "."
    app.run(debug=True)
