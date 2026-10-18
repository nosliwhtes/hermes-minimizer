# Minimizer example media

- `minimizer-demo.png`: 1200 × 600 static poster / reduced-motion alternative.
- `minimizer-demo.gif`: 1200 × 600, 30 seconds, five editorial stills, looping.
- `minimizer-demo.mp4`: 1200 × 600, 30 seconds, H.264 / yuv420p, 10 fps, no audio.

## Provenance and limits

This is a **scripted walkthrough of authored illustrative fixtures**, not a live LLM recording, simulated agent run, or plugin-vs-baseline benchmark. Every frame carries that disclosure. Timing is editorial, not measured model latency. The install command is displayed for reference and was not executed by the renderer.

Minimizer contributes static guidance; it does not automatically review, edit, or enforce outcomes. The shown source is copied from `examples/ordered_dedup/after.py` and `examples/single_renderer/after.py`. The verifier actually ran locally before rendering and exited 0: two tests OK, ordered_dedup 12 → 6 physical lines, single_renderer 21 → 9, both behavior PASS. Counts include blank lines, comments, and imports. These observations concern the fixtures, not model effectiveness, performance, or token savings.

The visuals are generated locally with Pillow, existing DejaVu fonts, and FFmpeg. No generated photography, audio, external media, model calls, credentials, paid services, or new application dependencies are involved.

## Reproduce the illustrated checks

From a clean clone, run:

```bash
python examples/check.py
```

The four fixture sources and their checks are published in `examples/`; the images and video are pre-rendered documentation, not an executable asset pipeline or plugin runtime code. If a fixture changes, rerun the checks, recount the complete source files, and replace any media whose content or counts no longer match.

The walkthrough uses five editorial stills held for 4 / 8 / 8 / 6 / 4 seconds. Verification included GIF duration totals, MP4 dimensions/duration/codec/pixel format, nonempty output, encoded first/last frames, all scene midpoints, and a 600px-wide visual inspection for disclosure legibility, source/output readability, contrast, and clipping.
