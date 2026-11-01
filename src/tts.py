import asyncio, os, edge_tts
VOICE=os.getenv("TTS_VOICE","en-IN-NeerjaNeural")
async def _save(text,path):
    await edge_tts.Communicate(text=text,voice=VOICE,rate="-3%").save(str(path))
def render(text,path):
    if text and text.strip(): asyncio.run(_save(text,path))
