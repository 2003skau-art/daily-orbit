import os, boto3
from pathlib import Path
from xml.sax.saxutils import escape

def upload(path,key):
    names=("R2_ACCOUNT_ID","R2_ACCESS_KEY_ID","R2_SECRET_ACCESS_KEY","R2_BUCKET","R2_PUBLIC_BASE_URL")
    if any(not os.getenv(n) for n in names): raise RuntimeError("Missing R2 configuration")
    c=boto3.client("s3",endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
      aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],region_name="auto")
    c.upload_file(str(path),os.environ["R2_BUCKET"],key,ExtraArgs={"ContentType":"audio/mpeg","CacheControl":"public, max-age=31536000"})
    return os.environ["R2_PUBLIC_BASE_URL"].rstrip("/")+"/"+key

def write_feed(items):
    base=os.environ["PUBLIC_FEED_BASE_URL"].rstrip("/")
    entries=[]
    for x in items:
        entries.append(f"<item><title>{escape(x['title'])}</title><description>{escape(x['description'])}</description><enclosure url=\"{escape(x['audio_url'])}\" length=\"{x['length']}\" type=\"audio/mpeg\"/><guid isPermaLink=\"false\">{escape(x['guid'])}</guid><pubDate>{escape(x['pub_date'])}</pubDate></item>")
    xml='<?xml version="1.0" encoding="UTF-8"?>\n'+f"<rss version=\"2.0\" xmlns:itunes=\"http://www.itunes.com/dtds/podcast-1.0.dtd\"><channel><title>Daily Orbit – Your Commute Radio</title><link>{escape(base)}</link><description>Weekday devotion, planetary reflection and sourced news.</description><language>en-IN</language><itunes:author>Daily Orbit</itunes:author><itunes:explicit>false</itunes:explicit>{''.join(entries)}</channel></rss>"
    Path("feed").mkdir(exist_ok=True); Path("feed/podcast.xml").write_text(xml,encoding="utf-8")
