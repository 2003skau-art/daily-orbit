# Daily Orbit Radio – starter implementation

## What it does
Weekday RSS collection → one Groq story-selection call → one OpenRouter script call → deterministic validation → speech synthesis → MP3 → Cloudflare R2 → podcast RSS on GitHub Pages.

## Free-tier and reliability caveats
- OpenRouter free variants are currently limited to 50 requests/day for accounts that have not bought credits; failed requests count. One call is made per episode. Free models and limits change: see https://openrouter.ai/pricing and https://openrouter.ai/docs/api-reference/limits.
- Groq quotas depend on model and account; inspect https://console.groq.com/docs/rate-limits.
- R2 Standard currently includes a monthly free allowance of 10 GB-month storage, 1M Class A operations and 10M Class B operations; egress is free. Check https://developers.cloudflare.com/r2/pricing/.
- GitHub scheduled workflows may run late; 04:50 is a target, not a guaranteed delivery deadline.
- TTS uses the no-key Edge TTS endpoint and voice `en-IN-NeerjaNeural`. It is convenient for a prototype but is not a guaranteed free commercial API or SLA. For stricter self-hosting, replace `src/tts.py` with Piper/Kokoro and test CPU runtime/voice availability.
- ChatGPT subscriptions do not include automated OpenAI API moderation. The included validator checks structure, URLs, duplicates and word limits; it is not a factual guarantee or human editor.
- News summaries are based on RSS snippets, not full article verification. For high-stakes politics, manually inspect sources and add independent corroboration.

## Setup
1. Create a GitHub repository and upload these files to its default branch.
2. Create Groq and OpenRouter API keys.
3. Create a Cloudflare R2 bucket and configure public read access through a custom domain or public bucket URL.
4. Add GitHub Actions repository secrets: `GROQ_API_KEY`, `OPENROUTER_API_KEY`, `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`.
5. Add GitHub Actions variables: `R2_PUBLIC_BASE_URL` and `PUBLIC_FEED_BASE_URL` (example `https://USERNAME.github.io/daily-orbit-radio`).
6. Enable GitHub Pages: Settings → Pages → Deploy from branch → default branch → `/feed`.
7. Add your licensed audio files:
   - `assets/hanuman_chalisa.mp3`
   - `assets/planetary_music/moon.mp3`
   - `assets/planetary_music/mars.mp3`
   - `assets/planetary_music/mercury.mp3`
   - `assets/planetary_music/jupiter.mp3`
   - `assets/planetary_music/venus.mp3`
8. Run Actions → Daily Orbit → Run workflow once manually.
9. Subscribe in Apple Podcasts → Library → menu → Add a Show by URL → `https://USERNAME.github.io/daily-orbit-radio/podcast.xml`.

## Schedule and content
Cron `20 23 * * 0-4` targets 04:50 Asia/Kolkata, Monday-Friday. Planet sequence is Moon, Mars, Mercury, Jupiter, Venus. Five news categories are configured: Bengaluru, India, Global politics, Business & technology, Science & world. Up to four stories per category.

## Audio rights
Only upload devotional/planetary recordings that you have permission to reproduce and distribute in a podcast. The starter does not download or supply copyrighted music. The Chalisa meaning is original reflection, not a reproduction of lyrics.

## Operational notes
Run manually for several days before relying on it. Verify voice, pronunciation, story accuracy, RSS validity, R2 public access and total runtime. The starter currently concatenates the provided music assets and narration, but does not guarantee a 45–50 minute runtime; it should never pad with invented content. Consider R2 retention cleanup if your archive grows beyond the free allowance.
