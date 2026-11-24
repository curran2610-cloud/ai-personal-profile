# PPT Motion Workflow

## Source Of Truth

- Source PPT: `assets/source/过往思路学习_内训汇总.pptx`
- Slide images: `assets/slides/slide-01.png` through `slide-16.png`
- Slide manifest: `specs/slide-manifest.json`
- Narration/caption plan: `specs/narration-script.json`
- Human-readable narration: `specs/narration-script.txt`
- Editable motion plan: `specs/motion-plan.yaml`
- Visual rules: `DESIGN.md`
- Generated HyperFrames entry: `index.html`

## Regenerate Assets

If the PPT changes, rerun:

```bash
/Users/kunkun/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/soffice -env:UserInstallation=file:///Users/kunkun/Documents/工作AI知识库搭建/ppt-motion-project/review/lo-profile --headless --convert-to pdf --outdir /Users/kunkun/Documents/工作AI知识库搭建/ppt-motion-project/assets/source /Users/kunkun/Documents/工作AI知识库搭建/ppt-motion-project/assets/source/过往思路学习_内训汇总.pptx
/Users/kunkun/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/pdftoppm -png -r 144 /Users/kunkun/Documents/工作AI知识库搭建/ppt-motion-project/assets/source/过往思路学习_内训汇总.pdf /Users/kunkun/Documents/工作AI知识库搭建/ppt-motion-project/assets/slides/slide
/Users/kunkun/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/extract_pptx_manifest.py assets/source/过往思路学习_内训汇总.pptx assets/slides specs
/Users/kunkun/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/create_narration_script.py specs/slide-manifest.json specs
```

## Rebuild Composition

```bash
/Users/kunkun/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/sync_narration_to_audio.py
/Users/kunkun/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/build_hyperframes_from_manifest.py specs/slide-manifest.json index.html
```

If `specs/narration-script.json` exists, the builder uses it for slide durations, chapter labels, caption text, keyword chips, and any `audio_path` clips synced from `assets/audio/gemini/audio-manifest.json`. If it is removed, the builder falls back to `specs/slide-manifest.json` durations and the simpler v1 visual treatment.

## Check

```bash
npm run check
```

Current expected result:

- `0 error(s)` in lint
- `0 layout issues` in inspect
- Validate may warn that wav metadata was not read within the timeout, but the render pipeline still detects and processes the 16 audio clips; confirm the final MP4 with `ffprobe` when audio timing changes.
- Three maintainability warnings remain because this first pass keeps all 16 slides in one root composition. Split into sub-compositions when per-slide animation becomes more detailed.

## Preview

```bash
npm run dev -- --port 3017
```

Studio URL:

```text
http://localhost:3017/#project/ppt-motion-project
```

## Render Draft

```bash
npm run render -- --quality draft --output renders/draft/过往思路学习_内训汇总_motion_draft.mp4
```

Current v2 caption-enhanced draft:

```bash
npm run render -- --quality draft --output renders/draft/过往思路学习_内训汇总_motion_v2_caption_draft.mp4
```

Current v3 Gemini voice draft:

```bash
npm run render -- --quality draft --output renders/draft/过往思路学习_内训汇总_motion_v3_voice_draft.mp4
```

## Render Final

```bash
npm run render -- --quality high --output renders/final/过往思路学习_内训汇总_motion_final.mp4
```

## Control Points

- Change slide pacing in `specs/motion-plan.yaml`, then mirror the selected values into `specs/slide-manifest.json` or extend the build script to read YAML directly.
- Change narration pacing, captions, keywords, and chapter labels in `specs/narration-script.json`.
- Change global colors and motion rules in `DESIGN.md`.
- Change actual generated motion behavior in `scripts/build_hyperframes_from_manifest.py`.
- Do not hand-edit `index.html` for durable changes; regenerate it from the script.

## Voiceover

The current voice pipeline uses the DataEyes relay with Gemini native TTS. Set `OPENAI_API_KEY` and `OPENAI_BASE_URL` locally. Do not paste the key into chat.

Configure the key:

```bash
scripts/configure_openai_key.sh
```

Verify CLI wiring without making an API call:

```bash
scripts/tts_dry_run.sh
```

Generate Gemini TTS:

```bash
/Users/kunkun/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/generate_gemini_tts.py --model gemini-3.1-flash-tts-preview --voice Kore
```

Then sync audio durations and rebuild:

```bash
/Users/kunkun/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/sync_narration_to_audio.py
/Users/kunkun/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/build_hyperframes_from_manifest.py specs/slide-manifest.json index.html
```

Generated audio stays under `assets/audio/`, and `index.html` receives timed `<audio>` clips on track 3. Rerun `npm run check` before final render.
