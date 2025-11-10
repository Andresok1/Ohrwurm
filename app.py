
import os
import requests
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__)

SPOTIFY_CLIENT_ID = os.environ.get("64f51e964a934cebba73cd24fd432348")
SPOTIFY_CLIENT_SECRET = os.environ.get("59e3a2e6e51f422094717076908afb4a")
PLAYLIST_ID = "TU_PLAYLIST_ID_AQUI"  # por ejemplo "37i9dQZF1DXcBWIGoYBM5M"

def get_access_token():
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        raise RuntimeError("Spotify client id or secret not set")

    url = "https://accounts.spotify.com/api/token"
    data = {"grant_type": "client_credentials"}
    resp = requests.post(url, data=data, auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET))
    token_data = resp.json()
    return token_data["access_token"]

@app.route("/api/playlist")
def get_playlist_tracks():
    if not PLAYLIST_ID:
        return jsonify({"error": "PLAYLIST_ID not configured"}), 500
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks"
    resp = requests.get(url, headers=headers)

    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": "Spotify API error", "details": str(e), "body": resp.text}), 500
    
    data = resp.json()

    tracks_clean = []
    for item in data.get("items", []):
        track = item.get("track")
        if track is None:
            continue

        album = track.get("album", {})
        images = album.get("images", [])
        image_url = images[0]["url"] if images else None

        tracks_clean.append(
            {
                "title": track.get("name"),
                "artist": ", ".join(a["name"] for a in track.get("artists", [])),
                "url": track.get("external_urls", {}).get("spotify"),
                "album_image": image_url,
            }
        )

    return jsonify(tracks_clean)

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


if __name__ == "__main__":
    app.run(debug=True)
