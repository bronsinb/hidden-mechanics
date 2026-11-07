"""Upload ready episodes to YouTube with the official Data API (run by GitHub Actions).

Queue = pipeline/episodes.json. An entry with "status": "ready" gets uploaded:
  video      path of the MP4 in the repo (e.g. videos/hidden_mechanics_03_slug.mp4)
  publish_at RFC3339 time to go public (e.g. 2026-11-08T10:00:00-08:00); past/missing = public now
Title, description and tags come from pipeline/episodes/NN_slug/meta.json.
On success the entry becomes "status": "scheduled" (or "published") with youtube_id and video_url.

Secrets (GitHub repo settings): YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN.
`python pipeline/publish.py check` only verifies the login and prints the channel name.
"""
import json, os, sys, datetime as dt
import urllib.request, urllib.parse, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "pipeline", "episodes.json")
CHANNEL_ID = "UCqTSZ70ZSh30bof-sx5kROQ"


def http(method, url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


def token():
    missing = [k for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN") if not os.environ.get(k)]
    if missing:
        sys.exit(f"Missing repo secrets: {', '.join(missing)}")
    body = urllib.parse.urlencode({
        "client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"}).encode()
    st, _, out = http("POST", "https://oauth2.googleapis.com/token", body,
                      {"Content-Type": "application/x-www-form-urlencoded"})
    if st != 200:
        sys.exit(f"Google login failed ({st}): {out.decode()[:300]}  -> the refresh token may be expired or revoked.")
    return json.loads(out)["access_token"]


def check(tok):
    st, _, out = http("GET", "https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true",
                      headers={"Authorization": f"Bearer {tok}"})
    if st != 200:
        sys.exit(f"Channel lookup failed ({st}): {out.decode()[:300]}")
    items = json.loads(out).get("items", [])
    for it in items:
        print(f"Logged in as channel: {it['snippet']['title']} ({it['id']})")
    if not any(it["id"] == CHANNEL_ID for it in items):
        sys.exit(f"Warning: the login is not for the Hidden Mechanics channel ({CHANNEL_ID}). Re-authorize with that channel selected.")


def upload(tok, ep):
    meta_dir = os.path.join(ROOT, "pipeline", "episodes", f"{ep['n']:02d}_{ep['slug']}")
    meta = json.load(open(os.path.join(meta_dir, "meta.json")))
    path = os.path.join(ROOT, ep["video"])
    size = os.path.getsize(path)
    now = dt.datetime.now(dt.timezone.utc)
    status = {"selfDeclaredMadeForKids": False, "containsSyntheticMedia": False, "embeddable": True,
              "license": "youtube", "publicStatsViewable": True}
    pub = ep.get("publish_at")
    pub_t = dt.datetime.fromisoformat(pub) if pub else None
    if pub_t and pub_t > now + dt.timedelta(minutes=15):
        status.update({"privacyStatus": "private", "publishAt": pub_t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
    else:
        status["privacyStatus"] = "public"
    body = {"snippet": {"title": meta["title"][:100], "description": meta["description"][:4900],
                        "tags": meta.get("tags", [])[:30], "categoryId": "28", "defaultLanguage": "en",
                        "defaultAudioLanguage": "en"},
            "status": status}
    st, hd, out = http("POST", "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
                       json.dumps(body).encode(), {"Authorization": f"Bearer {tok}",
                                                   "Content-Type": "application/json; charset=UTF-8",
                                                   "X-Upload-Content-Type": "video/mp4",
                                                   "X-Upload-Content-Length": str(size)})
    if st != 200:
        sys.exit(f"Upload start failed for #{ep['n']} ({st}): {out.decode()[:500]}")
    loc = hd.get("Location") or hd.get("location")
    with open(path, "rb") as fh:
        st, _, out = http("PUT", loc, fh.read(), {"Content-Type": "video/mp4", "Content-Length": str(size)})
    if st not in (200, 201):
        sys.exit(f"Upload failed for #{ep['n']} ({st}): {out.decode()[:500]}")
    vid = json.loads(out)["id"]
    ep["youtube_id"] = vid
    ep["video_url"] = f"https://youtube.com/shorts/{vid}"
    ep["status"] = "scheduled" if "publishAt" in status else "published"
    ep["uploaded_at"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"#{ep['n']} uploaded: {ep['video_url']} ({ep['status']}, publish_at {status.get('publishAt', 'now')})")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check(token())
        return
    log = json.load(open(LOG))
    ready = [e for e in log if e.get("status") == "ready"]
    if not ready:
        print("Nothing to upload.")
        return
    tok = token()
    for ep in ready:
        upload(tok, ep)
        json.dump(log, open(LOG, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
