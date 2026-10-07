# Editable technical film

Twelve HyperFrames scenes follow a continuous 142-second English narration. The technical section is a schematic animation grounded in the actual model path; its lines are not attention maps or measured internal activations. The source imagery and scores are the recorded evidence cases.

## Prepare and render

Install Node.js 22+, Python 3.10+, FFmpeg and curl. From the repository root:

```sh
cd video
npm install
cd ..
python scripts/prepare_video.py
cd video
npm run check
npm run dev
# In another terminal, from video/:
npm run render -- --output receiving-evidence.mp4
```

Preparation downloads four licensed source clips and verifies their hashes, creates the film crops, and decodes the included continuous narration. The default browser demo does not require these downloads.

The source edition omits the music bed because standalone music is not redistributed. The finished video in the GitHub release includes the licensed mix. Narration and scene timing are preserved. The compiler resolves Montserrat and IBM Plex Mono fonts; see their upstream licenses.

`timing.json` lists the scene boundaries. `compositions/` contains each editable scene and a single caption track. `../docs/narration-en.txt` and `.srt` contain the exact continuous script and captions. The diagrams adapt the real-length SVG connector pattern from HyperFrames' constellation-hub primitive.
