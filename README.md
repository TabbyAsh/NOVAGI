# NovaCut — Local AI Video Editor

NovaCut turns long raw recordings into ranked, editable highlight clips using local audio, visual, scene, motion, transcript, emotional-language, hook, conflict, reaction, and payoff signals.

It requires **no Claude subscription, Codex credits, paid API key, or cloud video upload**.

## Install on Windows

1. Click the green **Code** button above.
2. Click **Download ZIP**.
3. Extract the downloaded repository ZIP.
4. Double-click **`INSTALL_NOVACUT.bat`**.

The installer reconstructs the original NovaCut package from the included payload, verifies its SHA-256 integrity, extracts it, and opens the editor.

Windows may display a SmartScreen warning because this is an unsigned batch/PowerShell installer. Choose **More info → Run anyway** only after confirming that you downloaded it from this repository.

## Use NovaCut

After installation, use `NovaCut\NOVACUT.bat`:

- Double-click it to open the video picker and settings window.
- Or drag a video directly onto it for an automatic gaming-profile run.

The first launch creates a private Python environment and downloads free local dependencies. The first transcription run downloads the chosen Whisper model once. Later runs reuse the local installation and model.

## Output

For a source such as `recording.mp4`, NovaCut creates a results folder containing:

- Ranked horizontal clips
- Ranked vertical 9:16 clips
- Burned captions and editable `.srt` subtitles
- An HTML review report
- Detailed JSON analysis and component scores

## What the first version detects

- Audio energy and sudden peaks
- Speech and timestamped transcript content
- Emotional and surprising language
- Hooks, conflict, reactions, and payoff language
- Visual motion and scene changes
- Duplicate/overlapping candidate suppression

## Privacy and cost

- No paid API
- No footage upload to an editing service
- Processing stays on your computer
- Free local/open-source components

## Integrity

The reconstructed `NovaCut.zip` must match:

`2959c60a725d48e6db3e20cb78da516e986972a889638f272273f8cfc65a5226`

The installer refuses to extract or run the package if the hash does not match.
