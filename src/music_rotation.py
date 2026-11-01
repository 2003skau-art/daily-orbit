
import json
from pathlib import Path

MUSIC_DIR = Path("assets/planetary_music")
STATE_FILE = Path("data/music_rotation.json")


def select_planet_track(planet):
    """Choose the next track without advancing the saved rotation."""
    planet = planet.lower()
    folder = MUSIC_DIR / planet

    tracks = sorted(
        (p for p in folder.glob("*.mp3") if p.is_file()),
        key=lambda p: p.name.lower()
    )

    if not tracks:
        raise FileNotFoundError(
            f"No MP3 tracks found in {folder}"
        )

    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    else:
        state = {}

    last_played = state.get(planet)

    if last_played:
        previous = next(
            (i for i, track in enumerate(tracks)
             if track.name == last_played),
            None
        )
        next_index = (previous + 1) % len(tracks) if previous is not None else 0
    else:
        next_index = 0

    return tracks[next_index]


def record_planet_track(planet, selected_track):
    """Save the track only after its episode has been published."""
    planet = planet.lower()

    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    else:
        state = {}

    state[planet] = Path(selected_track).name

    STATE_FILE.write_text(
        json.dumps(state, indent=2),
        encoding="utf-8"
    )
