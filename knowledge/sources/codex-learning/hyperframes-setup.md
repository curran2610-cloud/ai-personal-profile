# HyperFrames installation follow-up note

Date: 2026-06-30

User asked to remember the HyperFrames setup state and use it for future self-checks if related problems occur. [ad-hoc note]

Installed and verified:
- Codex plugin `hyperframes@openai-curated` is installed and enabled, plugin cache id observed as `3fdeeb49`. [ad-hoc note]
- HyperFrames CLI `npx -y hyperframes doctor` reported version `0.7.21`. [ad-hoc note]
- Node.js satisfied HyperFrames requirement; final interactive zsh doctor used Node `v22.22.3`, while system checks also showed newer Node versions available. [ad-hoc note]
- FFmpeg and FFprobe were installed through Homebrew and verified as `8.1.2` at `/opt/homebrew/bin/ffmpeg` and `/opt/homebrew/bin/ffprobe`. [ad-hoc note]
- Chrome Headless Shell download repeatedly failed due network `ECONNRESET`, including one attempt that reached about 91 percent. [ad-hoc note]
- As a working fallback, `HYPERFRAMES_BROWSER_PATH` was set in `/Users/kunkun/.zshrc` to `/Applications/Doubao.app/Contents/Helpers/Doubao Browser.app/Contents/MacOS/Doubao Browser`; HyperFrames doctor accepted this as Chrome via env. [ad-hoc note]

Known unfinished or optional items to self-check later:
- Optional HyperFrames doctor failures were intentionally left unresolved: Docker not installed/running, whisper-cpp not installed, Kokoro local TTS not installed, MusicGen/BGM stack not installed. These are optional unless the user needs Docker rendering, transcription, local voice fallback, or local music fallback. [ad-hoc note]
- If future rendering has Chrome-specific failures, first verify `echo $HYPERFRAMES_BROWSER_PATH`, confirm the Doubao Browser executable still exists, then rerun `npx -y hyperframes doctor`. If the fallback breaks, try installing official Chrome Headless Shell again with `npx -y hyperframes browser ensure` or install Google Chrome/Chrome for Testing and point `HYPERFRAMES_BROWSER_PATH` to it. [ad-hoc note]
- If future audio/transcription/music workflows fail, inspect doctor output and install only the relevant optional dependency rather than all optional tools at once. [ad-hoc note]
