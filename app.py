from flask import Flask, render_template, request
import os
import openai
import moviepy.editor as mp
import requests
import json
import os
import tiktoken

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
# API キーを設定
openai.api_key = os.environ.get("OPENAI_API_KEY")
Model = "gpt-3.5-turbo"
TokenLength = 4096

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


def split_text(text, max_tokens):
    encoding = tiktoken.encoding_for_model(Model)

    tokens =  encoding.encode(text)
    token_length = len(tokens)

    # トークン数がmax_tokensを超える場合は、max_tokensで分割
    split_num = token_length // max_tokens + 1
    if split_num == 0:
        return [text]

    chunks = []
    temp = ""
    num = 0
    for c in text:
        print(c, len(text), split_num, num, token_length)
        if len(text)/split_num > num:
            temp += c
            num += 1
        else:
            chunks.append(temp)
            temp = ""
            num = 0
    
    chunks.append(temp)
    return chunks

@app.route("/summary", methods=["GET"])
def summary():
    text = "北海道大学では、今日、新型コロナウイルスの感染対策として、午前と午後の2回に分けて入学式が行われ、2546人の新入学生のうち、およそ7割が同外出身者です。北京清浜総長は、ビーアンビシャスの精神に思いをめぐらせてほしいとエールを送りました。新入生たちは、これから始まるエルムの森での大学生活に向けて、期待に胸を膨らませていました。"
    chunks = split_text(text, 60)
    print(chunks)
    return text

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.config.from_pyfile("config.py")
    app.run(debug=True)
