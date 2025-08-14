# --- المكتبات الأساسية ---
import sys
from flask import Flask, request, jsonify
import requests

# --- تهيئة تطبيق فلاسك ---
app = Flask(__name__)

# نفس الـ headers التي ذكرتها
HEADERS = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.7",
    "origin": "https://111movies.com",
    "priority": "u=1, i",
    "referer": "https://111movies.com/",
    "sec-ch-ua": '"Not;A=Brand";v="99", "Brave";v="139", "Chromium";v="139"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "sec-gpc": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
}

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Subtitle API is running!",
        "endpoints": {
            "movie_subtitles": "/subs?type=movie&id={tmdb_id}",
            "tv_subtitles": "/subs?type=tv&id={tmdb_id}&season={season}&episode={episode}"
        },
        "examples": {
            "movie": "/subs?type=movie&id=872585",
            "tv": "/subs?type=tv&id=1399&season=1&episode=1"
        }
    })

@app.route("/subs", methods=["GET"])
def get_subtitles():
    content_type = request.args.get("type")  # movie أو tv
    tmdb_id = request.args.get("id")
    season = request.args.get("season")
    episode = request.args.get("episode")

    if not content_type or not tmdb_id:
        return jsonify({"error": "يجب إدخال type و id"}), 400

    # بناء الرابط
    if content_type == "movie":
        url = f"https://sub.wyzie.ru/search?id={tmdb_id}&format=srt"
    elif content_type == "tv":
        if not season or not episode:
            return jsonify({"error": "يجب إدخال season و episode للمسلسل"}), 400
        url = f"https://sub.wyzie.ru/search?id={tmdb_id}&season={season}&episode={episode}&format=srt"
    else:
        return jsonify({"error": "type يجب أن يكون movie أو tv"}), 400

    # إرسال الطلب
    resp = requests.get(url, headers=HEADERS)

    try:
        data = resp.json()
    except Exception:
        data = resp.text

    return jsonify({"url": url, "status": resp.status_code, "response": data})

# Export the Flask app for Vercel
app.debug = True