# NovaCut — Local AI Video Editor

NovaCut turns long raw recordings into ranked highlight clips using local audio energy, transcript emotion, hooks, conflict, reactions, and payoff signals.

It requires **no Claude subscription, Codex credits, paid API key, or cloud video upload**.

## Download and run on Windows

1. Click **Code → Download ZIP** on this repository.
2. Extract the downloaded ZIP.
3. Open the extracted folder.
4. Double-click **`NOVACUT.bat`**.
5. Choose your raw video.

You can also drag a video directly onto `NOVACUT.bat`.

**Do not run the old `INSTALL_NOVACUT.bat`.** It belonged to a failed payload-delivery workaround and is no longer needed. NovaCut now runs directly from the repository files.

## First launch

The launcher creates a private Python environment and installs the free local dependencies. The first transcription run downloads the selected Whisper model once; later runs reuse it locally.

If Python is not installed, the launcher opens the official Python download page. Install Python 3.10 or newer with **Add Python to PATH** enabled, then run `NOVACUT.bat` again.

## Output

Beside a source such as `recording.mp4`, NovaCut creates `recording_NovaCut` containing:

- Ranked horizontal MP4 clips
- Ranked vertical 9:16 MP4 clips
- Editable `.srt` subtitle files
- `review.html`
- `analysis.json` with timestamps, text, and scores

## Privacy and cost

- No paid API
- No footage upload to an editing service
- Processing stays on your computer
- Free local/open-source components
