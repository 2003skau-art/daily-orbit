
import os
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape

import requests


def upload(path, key):
    token = os.getenv("GH_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    if not token or not repo:
        raise RuntimeError("Missing GH_TOKEN or GITHUB_REPOSITORY")

    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)

    # Use a simple filename for the GitHub Release asset.
    filename = path.name
    date = Path(key).stem
    tag = f"daily-orbit-{date}"

    api = f"https://api.github.com/repos/{repo}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    # Find an existing release, or create one.
    response = requests.get(
        f"{api}/releases/tags/{quote(tag, safe='')}",
        headers=headers,
        timeout=30,
    )

    if response.status_code == 404:
        response = requests.post(
            f"{api}/releases",
            headers=headers,
            json={
                "tag_name": tag,
                "name": f"Daily Orbit – {date}",
                "body": f"Daily Orbit commute episode for {date}.",
                "draft": False,
                "prerelease": False,
            },
            timeout=30,
        )

    response.raise_for_status()
    release = response.json()
    release_id = release["id"]

    # Replace an existing asset if this episode is regenerated.
    for asset in release.get("assets", []):
        if asset["name"] == filename:
            deleted = requests.delete(
                f"{api}/releases/assets/{asset['id']}",
                headers=headers,
                timeout=30,
            )
            deleted.raise_for_status()

    # Upload the MP3 to the release.
    upload_url = (
        f"https://uploads.github.com/repos/{repo}/releases/"
        f"{release_id}/assets?name={quote(filename)}"
    )

    with path.open("rb") as audio:
        result = requests.post(
            upload_url,
            headers={
                **headers,
                "Content-Type": "audio/mpeg",
            },
            data=audio,
            timeout=(30, 900),
        )

    result.raise_for_status()
    return result.json()["browser_download_url"]


def write_feed(items):
    base = os.environ["PUBLIC_FEED_BASE_URL"].rstrip("/")
    entries = []

    for item in items:
        entries.append(
            f"<item>"
            f"<title>{escape(item['title'])}</title>"
            f"<description>{escape(item['description'])}</description>"
            f"<enclosure url=\"{escape(item['audio_url'])}\" "
            f"length=\"{item['length']}\" type=\"audio/mpeg\"/>"
            f"<guid isPermaLink=\"false\">{escape(item['guid'])}</guid>"
            f"<pubDate>{escape(item['pub_date'])}</pubDate>"
            f"</item>"
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" '
        'xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">'
        '<channel>'
        '<title>Daily Orbit – Your Commute Radio</title>'
        f'<link>{escape(base)}</link>'
        '<description>Weekday devotion, planetary reflection and sourced news.</description>'
        '<language>en-IN</language>'
        '<itunes:author>Daily Orbit</itunes:author>'
        '<itunes:explicit>false</itunes:explicit>'
        f'{"".join(entries)}'
        '</channel></rss>'
    )

    Path("feed").mkdir(exist_ok=True)
    Path("feed/podcast.xml").write_text(xml, encoding="utf-8")
