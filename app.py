import os
import tweepy
from flask import Flask, request, jsonify, render_template
from datetime import datetime, timezone
import math

app = Flask(__name__)

# --- Twitter/X Client ---
def get_twitter_client():
    key = os.environ.get("TWITTER_API_KEY", "MISSING")
    secret = os.environ.get("TWITTER_API_SECRET", "MISSING")
    token = os.environ.get("TWITTER_ACCESS_TOKEN", "MISSING")
    token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET", "MISSING")
    print(f"KEY={key[:6]}... SECRET={secret[:6]}... TOKEN={token[:6]}... TOKEN_SECRET={token_secret[:6]}...")
    return tweepy.Client(
        consumer_key=key,
        consumer_secret=secret,
        access_token=token,
        access_token_secret=token_secret,
    )


# --- State (in-memory, persists while server is running) ---
state = {
    "online": False,
    "online_since": None,
    "last_area": None,
    "last_song": None,
    "tweet_log": []
}

def hours_online():
    if not state["online_since"]:
        return 0
    delta = datetime.now(timezone.utc) - state["online_since"]
    return round(delta.total_seconds() / 3600, 1)

def post_tweet(text):
    try:
        client = get_twitter_client()
        client.create_tweet(text=text)
        state["tweet_log"].insert(0, {
            "text": text,
            "time": datetime.now(timezone.utc).strftime("%I:%M %p UTC")
        })
        # Keep log to last 20
        state["tweet_log"] = state["tweet_log"][:20]
        return True, None
    except Exception as e:
        return False, str(e)

# --- Secret key to protect endpoints ---
def check_secret(req):
    secret = os.environ.get("WEBHOOK_SECRET", "")
    provided = req.headers.get("X-Secret") or req.args.get("secret") or ""
    return provided == secret

# --- Endpoints ---

@app.route("/")
def dashboard():
    return render_template("dashboard.html", state=state, now=datetime.now(timezone.utc))

@app.route("/go-online", methods=["POST"])
def go_online():
    if not check_secret(request):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    area = data.get("area", "the city")
    song = data.get("song", None)
    artist = data.get("artist", None)

    state["online"] = True
    state["online_since"] = datetime.now(timezone.utc)
    state["last_area"] = area
    state["last_song"] = f"{song} - {artist}" if song and artist else song

    song_line = f"\n🎵 Playing: {state['last_song']}" if state["last_song"] else ""
    tweet = f"🚗 Just went online on Lyft!\n📍 Starting in {area}{song_line}"

    ok, err = post_tweet(tweet)
    if ok:
        return jsonify({"status": "tweeted", "tweet": tweet})
    else:
        return jsonify({"status": "error", "error": err}), 500

@app.route("/hourly-update", methods=["POST"])
def hourly_update():
    if not check_secret(request):
        return jsonify({"error": "Unauthorized"}), 401

    if not state["online"]:
        return jsonify({"status": "skipped", "reason": "Not currently online"})

    data = request.get_json(silent=True) or {}
    area = data.get("area", state["last_area"] or "the city")
    song = data.get("song", None)
    artist = data.get("artist", None)

    state["last_area"] = area
    state["last_song"] = f"{song} - {artist}" if song and artist else song

    hrs = hours_online()
    song_line = f"\n🎵 {state['last_song']}" if state["last_song"] else ""
    tweet = f"⏱️ {hrs}h online | Still rolling on Lyft\n📍 Currently in {area}{song_line}"

    ok, err = post_tweet(tweet)
    if ok:
        return jsonify({"status": "tweeted", "tweet": tweet})
    else:
        return jsonify({"status": "error", "error": err}), 500

@app.route("/go-offline", methods=["POST"])
def go_offline():
    if not check_secret(request):
        return jsonify({"error": "Unauthorized"}), 401

    hrs = hours_online()
    area = state.get("last_area") or "the city"

    tweet = f"🔴 Wrapped up for the day!\n⏱️ {hrs}h on the road\n📍 Last area: {area}\nThanks to everyone who rode with me 🙏"

    state["online"] = False
    state["online_since"] = None

    ok, err = post_tweet(tweet)
    if ok:
        return jsonify({"status": "tweeted", "tweet": tweet})
    else:
        return jsonify({"status": "error", "error": err}), 500

@app.route("/status")
def status():
    return jsonify({
        "online": state["online"],
        "hours_online": hours_online(),
        "last_area": state["last_area"],
        "last_song": state["last_song"],
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
