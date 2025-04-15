import os
from flask import Flask, send_from_directory, jsonify, request, render_template_string, abort
from flask_cors import CORS

MUSIC_DIR = "./music"

app = Flask(__name__)
CORS(app)

def get_tracks():
    files = [f for f in os.listdir(MUSIC_DIR) if f.endswith(".dfpwm")]
    tracks = []
    for f in sorted(files, key=lambda x: x.lower()):
        path = os.path.join(MUSIC_DIR, f)
        size = os.path.getsize(path)
        name = os.path.splitext(f)[0]
        track = {
            "filename": f,
            "title": name,
            "url": f"/music/{f}",
            "size": size
        }
        tracks.append(track)
    return tracks

STATS = {}

@app.route("/")
def index():
    tracks = get_tracks()
    html = """
    <html>
    <head>
        <title>DFPWM Music Server</title>
        <style>
            body { background: #24292e; color: #fff; font-family: sans-serif; margin: 40px;}
            h1 { color: #ffb347; }
            a { color: #61dafb; text-decoration: none;}
            .track { margin-bottom: 12px; }
        </style>
    </head>
    <body>
        <h1>DFPWM Music Files</h1>
        <ul>
        {% for t in tracks %}
            <li class="track">
                <b>{{ t.title }}</b>
                [<a href="{{ t.url }}">Get</a>]
                [<a href="{{ t.url }}" download="{{t.title}}.dfpwm">Download</a>]
                <span style="color:#888;">({{ t.size }} bytes)</span>
            </li>
        {% endfor %}
        </ul>
        <hr>
        <small>API: <a href="/tracks">/tracks</a></small>
    </body>
    </html>
    """
    return render_template_string(html, tracks=tracks)

@app.route("/tracks")
def track_list():
    return jsonify(get_tracks())

@app.route("/music/<path:filename>")
def music_file(filename):
    STATS[filename] = STATS.get(filename, 0) + 1
    if not os.path.exists(os.path.join(MUSIC_DIR, filename)):
        return abort(404, "File not found")
    return send_from_directory(MUSIC_DIR, filename)

@app.route("/stats")
def stats():
    return jsonify(STATS)

@app.route("/listen", methods=['POST'])
def listen():
    data = request.json
    filename = data.get("filename")
    if filename:
        STATS[filename] = STATS.get(filename, 0) + 1
    return jsonify({"ok": True, "filename": filename})

if __name__ == "__main__":
    os.makedirs(MUSIC_DIR, exist_ok=True)
    app.run(host="127.0.0.1", port=3000)