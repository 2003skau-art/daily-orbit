import feedparser, time, hashlib
from datetime import datetime, timedelta, timezone
from .config import CATEGORIES

def collect():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=36)
    results, seen = [], set()
    for cat in CATEGORIES:
        for feed in cat["feeds"]:
            parsed = feedparser.parse(feed)
            for e in parsed.entries[:30]:
                title, url = " ".join(e.get("title","").split()), e.get("link","").strip()
                if not title or not url:
                    continue
                ts = e.get("published_parsed") or e.get("updated_parsed")
                published = datetime.fromtimestamp(time.mktime(ts), timezone.utc) if ts else datetime.now(timezone.utc)-timedelta(days=2)
                key = hashlib.sha1((title.lower()+url).encode()).hexdigest()
                if published >= cutoff and key not in seen:
                    seen.add(key)
                    results.append({"category_id":cat["id"],"title":title[:300],
                        "summary":" ".join(e.get("summary","").split())[:800],
                        "url":url,"published":published.isoformat(),
                        "source":e.get("source",{}).get("title",url.split("/")[2])})
    return results
