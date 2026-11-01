import json
from pathlib import Path
from datetime import datetime, timezone
from email.utils import format_datetime
from .news_fetcher import collect
from .ai import groq, openrouter
from .editorial_moderator import moderate_stories, moderate_script
from .audio import make_audio
from .publish import upload, write_feed

PLANETS={0:"Moon",1:"Mars",2:"Mercury",3:"Jupiter",4:"Venus"}
def main():
    now=datetime.now().astimezone()
    if now.weekday()>4: print("Weekend; skipping."); return
    date=now.strftime("%Y-%m-%d"); planet=PLANETS[now.weekday()]
    raw=collect()
    if not raw: raise RuntimeError("No recent RSS stories; fail closed.")
    stories=moderate_stories(groq(raw))
    if not stories: raise RuntimeError("No stories passed validation.")
    script=moderate_script(openrouter(stories,planet))
    output=Path("work")/f"daily-orbit-{date}.mp3"
    minutes=make_audio(script,planet,date,output)
    audio_url=upload(output,f"episodes/{date}.mp3")
    episode={"title":f"Daily Orbit – {date} – {planet}","audio_url":audio_url,
      "length":str(output.stat().st_size),"guid":f"daily-orbit-{date}",
      "pub_date":format_datetime(datetime.now(timezone.utc)),
      "description":f"Commute edition · {planet} day · {minutes:.1f} minutes"}
    p=Path("feed/episodes.json"); old=json.loads(p.read_text()) if p.exists() else []
    old=[x for x in old if x["guid"]!=episode["guid"]]; old.insert(0,episode); old=old[:30]
    p.parent.mkdir(exist_ok=True); p.write_text(json.dumps(old,indent=2),encoding="utf-8")
    write_feed(old); print("Published",episode["title"],audio_url)
if __name__=="__main__": main()
