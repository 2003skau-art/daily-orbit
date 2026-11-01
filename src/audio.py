from pathlib import Path
from pydub import AudioSegment
from .tts import render

def make_audio(script, planet, date, output):
    work=Path("work")/date; work.mkdir(parents=True,exist_ok=True)
    parts=[]
    def say(name,text):
        p=work/f"{name}.mp3"; render(text,p)
        if p.exists(): parts.append(AudioSegment.from_file(p))
    say("intro",script["intro"])
    devotional=Path("assets/hanuman_chalisa.mp3")
    if devotional.exists(): parts.append(AudioSegment.from_file(devotional))
    say("meaning",script["chalisa_meaning"])
    say("planet_intro",script["planet_intro"])
    song=Path(f"assets/planetary_music/{planet.lower()}.mp3")
    if song.exists(): parts.append(AudioSegment.from_file(song))
    for i,s in enumerate(script["news_segments"]): say(f"news{i}",s["script"])
    say("closing",script["closing"])
    if not parts: raise RuntimeError("No audio was generated")
    final=AudioSegment.silent(500)
    for p in parts: final += p + AudioSegment.silent(400)
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    final.export(output,format="mp3",bitrate="96k")
    return len(final)/60000
