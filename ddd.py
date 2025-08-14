# --- المكتبات الأساسية ---
import sys
from flask import Flask, request, jsonify
import requests
import time
import random

# --- تهيئة تطبيق فلاسك ---
app = Flask(__name__)

# Headers مختلفة لتجنب الحظر
HEADERS_OPTIONS = [
    {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9,ar;q=0.8",
        "origin": "https://111movies.com",
        "referer": "https://111movies.com/",
        "sec-ch-ua": '"Not;A=Brand";v="99", "Brave";v="139", "Chromium";v="139"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    },
    {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.5",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
    },
    {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
]

# مصادر بديلة للترجمات
SUBTITLE_SOURCES = [
    "https://sub.wyzie.ru/search?id={tmdb_id}&format=srt",
    "https://sub.wyzie.ru/search?id={tmdb_id}&format=vtt",
    "https://sub.wyzie.ru/search?id={tmdb_id}&format=ass"
]

def try_multiple_sources(tmdb_id, content_type, season=None, episode=None):
    """تجربة مصادر متعددة للترجمات"""
    results = []
    
    for i, headers in enumerate(HEADERS_OPTIONS):
        for j, source_template in enumerate(SUBTITLE_SOURCES):
            try:
                # بناء الرابط
                if content_type == "movie":
                    url = source_template.format(tmdb_id=tmdb_id)
                else:
                    url = source_template.format(tmdb_id=tmdb_id) + f"&season={season}&episode={episode}"
                
                # إضافة تأخير عشوائي لتجنب الحظر
                time.sleep(random.uniform(0.5, 1.5))
                
                # إرسال الطلب
                resp = requests.get(url, headers=headers, timeout=15)
                
                result = {
                    "source": f"Source {j+1} with Headers {i+1}",
                    "url": url,
                    "status_code": resp.status_code,
                    "headers_used": f"Headers Set {i+1}",
                    "response": None
                }
                
                if resp.status_code == 200:
                    try:
                        result["response"] = resp.json()
                    except:
                        result["response"] = resp.text[:500] + "..." if len(resp.text) > 500 else resp.text
                else:
                    result["response"] = f"Error {resp.status_code}: {resp.reason}"
                
                results.append(result)
                
                # إذا نجح الطلب، إرجاع النتيجة
                if resp.status_code == 200:
                    return results
                    
            except Exception as e:
                results.append({
                    "source": f"Source {j+1} with Headers {i+1}",
                    "url": url if 'url' in locals() else "N/A",
                    "status_code": "Error",
                    "headers_used": f"Headers Set {i+1}",
                    "response": f"Exception: {str(e)}"
                })
    
    return results

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
        },
        "note": "This API tries multiple sources and headers to avoid blocking"
    })

@app.route("/subs", methods=["GET"])
def get_subtitles():
    content_type = request.args.get("type")  # movie أو tv
    tmdb_id = request.args.get("id")
    season = request.args.get("season")
    episode = request.args.get("episode")

    if not content_type or not tmdb_id:
        return jsonify({"error": "يجب إدخال type و id"}), 400

    if content_type not in ["movie", "tv"]:
        return jsonify({"error": "type يجب أن يكون movie أو tv"}), 400

    if content_type == "tv" and (not season or not episode):
        return jsonify({"error": "يجب إدخال season و episode للمسلسل"}), 400

    # تجربة مصادر متعددة
    results = try_multiple_sources(tmdb_id, content_type, season, episode)
    
    # البحث عن أفضل نتيجة
    best_result = None
    for result in results:
        if result["status_code"] == 200:
            best_result = result
            break
    
    return jsonify({
        "request_info": {
            "type": content_type,
            "tmdb_id": tmdb_id,
            "season": season,
            "episode": episode
        },
        "best_result": best_result,
        "all_attempts": results,
        "summary": {
            "total_attempts": len(results),
            "successful_attempts": len([r for r in results if r["status_code"] == 200]),
            "failed_attempts": len([r for r in results if r["status_code"] != 200])
        }
    })

# Export the Flask app for Vercel
app.debug = True