from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import tempfile
import wave
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
from imageio_ffmpeg import get_ffmpeg_exe

EMOTION_WORDS = {
    "amazing", "insane", "crazy", "unbelievable", "wow", "what", "no way",
    "hate", "love", "angry", "scared", "terrified", "excited", "finally",
    "actually", "never", "always", "best", "worst", "dead", "killed",
    "win", "won", "lost", "fail", "failed", "clutch", "perfect", "bro",
    "dude", "stop", "wait", "look", "listen", "why", "how", "secret",
}

@dataclass
class Clip:
    start: float
    end: float
    score: float
    energy: float
    transcript_score: float
    text: str


def run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "Command failed")


def duration(ffmpeg: str, video: Path) -> float:
    probe = subprocess.run([ffmpeg, "-i", str(video)], text=True, capture_output=True)
    text = probe.stderr
    marker = "Duration: "
    i = text.find(marker)
    if i < 0:
        raise RuntimeError("Could not determine video duration")
    raw = text[i + len(marker):].split(",", 1)[0]
    h, m, s = raw.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def extract_audio(ffmpeg: str, video: Path, wav_path: Path) -> None:
    run([ffmpeg, "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav_path)])


def audio_energy(wav_path: Path, seconds: int = 1) -> np.ndarray:
    with wave.open(str(wav_path), "rb") as wf:
        rate = wf.getframerate()
        samples = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32)
    block = max(1, rate * seconds)
    values = []
    for i in range(0, len(samples), block):
        chunk = samples[i:i + block]
        if len(chunk):
            values.append(float(np.sqrt(np.mean(np.square(chunk / 32768.0)))))
    arr = np.asarray(values, dtype=np.float32)
    if not len(arr):
        return np.zeros(1, dtype=np.float32)
    lo, hi = np.percentile(arr, [10, 95])
    return np.clip((arr - lo) / max(hi - lo, 1e-6), 0, 1)


def transcribe(wav_path: Path, model_name: str) -> list[dict]:
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel(model_name, device="auto", compute_type="int8")
        segments, _ = model.transcribe(str(wav_path), vad_filter=True, beam_size=3)
        return [{"start": float(s.start), "end": float(s.end), "text": s.text.strip()} for s in segments]
    except Exception as exc:
        print(f"Transcription unavailable; continuing with audio scoring: {exc}")
        return []


def transcript_value(text: str) -> float:
    lower = text.lower()
    hits = sum(1 for word in EMOTION_WORDS if word in lower)
    punctuation = text.count("!") * 0.5 + text.count("?") * 0.35
    caps = sum(1 for token in text.split() if len(token) > 2 and token.isupper()) * 0.4
    return min(1.0, hits * 0.16 + punctuation * 0.12 + caps * 0.1)


def make_candidates(total: float, energy: np.ndarray, segments: list[dict], clip_len: int) -> list[Clip]:
    candidates: list[Clip] = []
    step = max(8, clip_len // 3)
    for start in np.arange(0, max(total - 1, 1), step):
        end = min(total, start + clip_len)
        a, b = int(start), max(int(math.ceil(end)), int(start) + 1)
        e = float(np.mean(energy[a:min(b, len(energy))])) if a < len(energy) else 0.0
        peak = float(np.max(energy[a:min(b, len(energy))])) if a < len(energy) else 0.0
        overlapping = [s for s in segments if s["end"] >= start and s["start"] <= end]
        text = " ".join(s["text"] for s in overlapping).strip()
        t = transcript_value(text)
        speech = min(1.0, len(text.split()) / max(clip_len * 2.2, 1))
        score = 0.48 * e + 0.22 * peak + 0.22 * t + 0.08 * speech
        candidates.append(Clip(float(start), float(end), round(score, 4), round(e, 4), round(t, 4), text))
    return candidates


def select(candidates: list[Clip], count: int) -> list[Clip]:
    chosen: list[Clip] = []
    for clip in sorted(candidates, key=lambda c: c.score, reverse=True):
        overlap = False
        for old in chosen:
            intersection = max(0.0, min(clip.end, old.end) - max(clip.start, old.start))
            if intersection > 0.35 * min(clip.end - clip.start, old.end - old.start):
                overlap = True
                break
        if not overlap:
            chosen.append(clip)
        if len(chosen) >= count:
            break
    return chosen


def srt_time(value: float) -> str:
    ms = int(round(value * 1000))
    h, rem = divmod(ms, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def write_srt(path: Path, clip: Clip, segments: list[dict]) -> None:
    rows = []
    n = 1
    for seg in segments:
        if seg["end"] < clip.start or seg["start"] > clip.end:
            continue
        start = max(0.0, seg["start"] - clip.start)
        end = min(clip.end - clip.start, seg["end"] - clip.start)
        rows.append(f"{n}\n{srt_time(start)} --> {srt_time(end)}\n{seg['text']}\n")
        n += 1
    path.write_text("\n".join(rows), encoding="utf-8")


def render(ffmpeg: str, video: Path, clip: Clip, out: Path, vertical: bool) -> None:
    cmd = [ffmpeg, "-y", "-ss", f"{clip.start:.3f}", "-i", str(video), "-t", f"{clip.end - clip.start:.3f}"]
    if vertical:
        cmd += ["-vf", "scale=-2:1920,crop=1080:1920:(iw-1080)/2:0"]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "160k", str(out)]
    run(cmd)


def process(video: Path, clips: int, clip_len: int, model: str, vertical: bool) -> Path:
    ffmpeg = get_ffmpeg_exe()
    out_dir = video.with_name(video.stem + "_NovaCut")
    out_dir.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="novacut_") as tmp:
        wav_path = Path(tmp) / "audio.wav"
        print("Extracting audio...")
        extract_audio(ffmpeg, video, wav_path)
        total = duration(ffmpeg, video)
        print("Analyzing audio...")
        energy = audio_energy(wav_path)
        print("Transcribing locally...")
        segments = transcribe(wav_path, model)
        selected = select(make_candidates(total, energy, segments, clip_len), clips)
        if not selected:
            raise RuntimeError("No candidate clips could be created")
        for index, clip in enumerate(selected, 1):
            stem = f"{index:02d}_score_{clip.score:.3f}"
            print(f"Rendering {index}/{len(selected)}: {clip.start:.1f}s–{clip.end:.1f}s")
            render(ffmpeg, video, clip, out_dir / f"{stem}_horizontal.mp4", False)
            if vertical:
                render(ffmpeg, video, clip, out_dir / f"{stem}_vertical.mp4", True)
            write_srt(out_dir / f"{stem}.srt", clip, segments)
        (out_dir / "analysis.json").write_text(json.dumps({"source": str(video), "clips": [asdict(c) for c in selected]}, indent=2), encoding="utf-8")
        report = ["<html><body><h1>NovaCut Results</h1>"]
        for i, clip in enumerate(selected, 1):
            report.append(f"<h2>#{i} — score {clip.score:.3f}</h2><p>{clip.start:.1f}s–{clip.end:.1f}s</p><p>{clip.text}</p>")
        report.append("</body></html>")
        (out_dir / "review.html").write_text("\n".join(report), encoding="utf-8")
    return out_dir


def choose_file() -> Path | None:
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    name = filedialog.askopenfilename(title="Choose raw footage", filetypes=[("Video files", "*.mp4 *.mkv *.mov *.avi *.webm *.m4v"), ("All files", "*.*")])
    root.destroy()
    return Path(name) if name else None


def main() -> int:
    parser = argparse.ArgumentParser(description="NovaCut local AI highlight editor")
    parser.add_argument("video", nargs="?", type=Path)
    parser.add_argument("--clips", type=int, default=10)
    parser.add_argument("--length", type=int, default=35)
    parser.add_argument("--model", default="base.en")
    parser.add_argument("--no-vertical", action="store_true")
    args = parser.parse_args()
    video = args.video or choose_file()
    if not video:
        return 0
    if not video.exists():
        raise FileNotFoundError(video)
    out = process(video.resolve(), max(1, args.clips), max(12, args.length), args.model, not args.no_vertical)
    print(f"\nFinished. Results: {out}")
    try:
        import os
        os.startfile(out)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
