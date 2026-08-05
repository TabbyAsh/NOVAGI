# NovaCut

NovaCut is a **local-first AI-assisted video editor** that turns long raw recordings into a ranked folder of promising clips. It does not call a paid API and does not upload the recording to an editing service.

## Download

Use the **Code → Download ZIP** button on this repository, then extract it and run `NOVACUT.bat` on Windows.

## Use it

1. Extract the downloaded ZIP.
2. Double-click **`NOVACUT.bat`**.
3. Choose a recording and click **Find Highlights**.

Or drag a video directly onto `NOVACUT.bat` for an automatic Gaming-profile run.

The launcher creates its own private Python environment and installs everything automatically. The first transcription run downloads the selected Whisper speech model once. After that, the model is reused locally.

## Output

For `recording.mp4`, NovaCut creates a results folder containing ranked horizontal clips, vertical 9:16 clips, subtitle files, an HTML review report, and detailed JSON analysis.

## Privacy and cost

- No paid API key
- No Claude or Codex subscription
- Processing stays on your computer
- Open-source local dependencies
