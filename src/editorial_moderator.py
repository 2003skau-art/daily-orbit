from urllib.parse import urlparse
import re

def moderate_stories(stories):
    out, seen = [], set()
    for s in stories:
        u=urlparse(s.get("url",""))
        title=re.sub(r"\\W+","",s.get("headline","").lower())
        if u.scheme not in ("http","https") or not u.netloc or not title: continue
        if title in seen or s.get("confidence")=="low" or not s.get("facts") or not s.get("source"): continue
        seen.add(title); out.append(s)
    return out

def moderate_script(data):
    for k in ("intro","chalisa_meaning","planet_intro","news_segments","closing"):
        if k not in data: raise ValueError(f"Missing script field: {k}")
    for s in data["news_segments"]:
        if not s.get("script") or not s.get("url"): raise ValueError("News segment missing source")
        if len(s["script"].split())>210: raise ValueError("Story exceeds 90-second word ceiling")
    return data
