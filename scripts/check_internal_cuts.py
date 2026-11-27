#!/usr/bin/env python3
"""
Scan one or more video clips (with optional in/out seconds) for internal hard scene cuts
using ffmpeg scene-change detection, preventing accidental <1.2s flash-cuts on the timeline.

Usage:
  python3 check_internal_cuts.py "clip.mov"
  python3 check_internal_cuts.py "clip.mov:33.8:40.8" "clip2.mov:1.0:5.6" --threshold 0.28
"""
import argparse
import subprocess
import sys


def scan_clip(spec: str, threshold: float) -> int:
    parts = spec.rsplit(":", 2)
    if len(parts) == 3:
        path, t0, t1 = parts
        cmd = ["ffmpeg", "-ss", t0, "-to", t1, "-i", path]
    else:
        path, t0, t1 = spec, None, None
        cmd = ["ffmpeg", "-i", path]

    cmd += ["-vf", f"select=gt(scene\\,{threshold}),showinfo", "-f", "null", "-"]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    cuts = []
    for line in res.stderr.splitlines():
        if "pts_time:" in line:
            for tok in line.split():
                if tok.startswith("pts_time:"):
                    cuts.append(tok.split(":", 1)[1])

    window = f"[{t0}-{t1}s]" if t0 is not None else "[full]"
    status = "PASS (0 cuts)" if not cuts else f"WARN ({len(cuts)} cuts: {', '.join(cuts)})"
    print(f"{path} {window} -> {status}")
    return len(cuts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect internal hard cuts in B-roll clips.")
    parser.add_argument("clips", nargs="+", help="Video path or path:start_sec:end_sec")
    parser.add_argument("--threshold", type=float, default=0.28, help="FFmpeg scene threshold (default: 0.28)")
    args = parser.parse_args()

    total_cuts = sum(scan_clip(c, args.threshold) for c in args.clips)
    sys.exit(1 if total_cuts > 0 else 0)


if __name__ == "__main__":
    main()
