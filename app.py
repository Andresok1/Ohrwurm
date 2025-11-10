
import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

SPOTIFY_CLIENT_ID = os.environ.get("64f51e964a934cebba73cd24fd432348")
SPOTIFY_CLIENT_SECRET = os.environ.get("59e3a2e6e51f422094717076908afb4a")
PLAYLIST_ID = "TU_PLAYLIST_ID_AQUI"  # por ejemplo "37i9dQZF1DXcBWIGoYBM5M"

def get_access_token():
    url = "https://accounts.spotify.com/api/token"
    data = {"grant_type": "client_credentials"}
    resp = requests.post(url, data=data, auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET))
    resp.raise_for_status()
    return resp.json()["access_token"]

@app.route("/api/playlist")
def get_playlist_tracks():
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()

    tracks_clean = []
    for item in data["items"]:
        track = item["track"]
        if track is None:
            continue

        album_images = track["album"]["images"]
        image_url = album_images[0]["url"] if album_images else None

        tracks_clean.append(
            {
                "title": track["name"],
                "artist": ", ".join(a["name"] for a in track["artists"]),
                "url": track["external_urls"]["spotify"],
                "album_image": image_url,
            }
        )

    return jsonify(tracks_clean)

if __name__ == "__main__":
    app.run(debug=True)
