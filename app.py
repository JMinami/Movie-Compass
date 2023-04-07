from flask import Flask, render_template, request
import os
import openai
import moviepy.editor as mp
import requests
import json
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
# API キーを設定
openai.api_key = os.environ.get("OPENAI_API_KEY")

def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        decoded_string = transcript["text"].encode("utf-8").decode("unicode_escape")
    return decoded_string

@app.route("/transcribe", methods=["POST"])
def transcribe_video():
    if "video" not in request.files:
        return "ファイルがありません", 400

    video = request.files["video"]
    if video.filename == "":
        return "ファイル名がありません", 400

    video_path = os.path.join(app.config["UPLOAD_FOLDER"], video.filename)
    video.save(video_path)

    # 動画から音声を抽出
    clip = mp.VideoFileClip(video_path)
    audio_path = os.path.join(app.config["UPLOAD_FOLDER"], "audio.wav")
    clip.audio.write_audiofile(audio_path)

    # 音声をテキストに変換
    transcript = transcribe_audio(audio_path)

    # 不要なファイルを削除
    os.remove(video_path)
    os.remove(audio_path)

    return transcript



@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.config.from_pyfile("config.py")
    app.run(debug=True)
