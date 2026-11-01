
from pathlib import Path
from pydub import AudioSegment
from .tts import render
from .music_rotation import select_planet_track


def make_audio(script, planet, date, output):
    work = Path("work") / date
    work.mkdir(parents=True, exist_ok=True)

    devotional = Path("assets/hanuman_chalisa.mp3")
    if not devotional.is_file():
        raise FileNotFoundError(
            f"Hanuman Chalisa recording is missing: {devotional}"
        )

    # Select the next available track for this planet.
    song = select_planet_track(planet)

    parts = []

    def say(name, text):
        if not text or not text.strip():
            raise ValueError(f"Missing script section: {name}")

        audio_path = work / f"{name}.mp3"
        render(text, audio_path)

        if not audio_path.is_file() or audio_path.stat().st_size == 0:
            raise RuntimeError(
                f"Speech audio was not generated: {name}"
            )

        parts.append(AudioSegment.from_file(audio_path))

    say("intro", script["intro"])
    parts.append(AudioSegment.from_file(devotional))
    say("meaning", script["chalisa_meaning"])
    say("planet_intro", script["planet_intro"])
    parts.append(AudioSegment.from_file(song))

    for i, segment in enumerate(script["news_segments"]):
        say(f"news{i}", segment["script"])

    say("closing", script["closing"])

    if not parts:
        raise RuntimeError("No audio was generated")

    final = AudioSegment.silent(500)
    for part in parts:
        final += part + AudioSegment.silent(400)

    Path(output).parent.mkdir(parents=True, exist_ok=True)
    final.export(output, format="mp3", bitrate="96k")

    # Return the selected track so we can record it after publishing.
    return len(final) / 60000, song
