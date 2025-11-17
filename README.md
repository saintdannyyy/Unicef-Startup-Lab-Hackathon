# Wote — Ghana Sign Language (GSL) Platform

Wote is an integrated open-source platform for Harmonized Ghanaian Sign Language (GSL). It bundles:

- A Telegram game + dictionary bot (wotegslbot/) for solo practice and 2-player competitive quizzes.
- A React web frontend (sign_language/) with live webcam sign detection (MediaPipe / TF.js) and practice UI.
- An ML pipeline & data tools (signify-ghana/) for collecting, training and exporting GSL models.

Built for the UNICEF Startup Lab — awarded 3rd Place and Best AI Implementation.

Quick highlights

- Solo practice (3-question quick quizzes) and 2-player synchronized matches (speed + accuracy scoring).
- Dictionary with community contribution flow for missing signs.
- Web frontend with SignDetector (MediaPipe & TF.js) and mock mode for robust demos.
- ML training pipeline to convert collected landmark samples into TF/TFLite/TF.js models.
- Works with images (.png/.jpg/.jpeg) and videos (.mp4/.mov/.avi).

Repository layout

- wotegslbot/ — Telegram bot, game engine, DB and demo guides
  - bot_enhanced.py — main bot (polling + webhook-ready)
  - game_database.py — game/room/leaderboard logic
  - database.py — media/dictionary scanner
  - data/ — media assets and JSON resources
  - DEMO_GUIDE.md, VISUAL_SHOWCASE.md, tests
- sign_language/ — React (Vite) frontend and SignDetector components
  - src/components/SignDetector.tsx — MediaPipe + mock fallback
  - pages/PracticeEnhanced.tsx — Duolingo-style UI
  - public/assets/web_model/ — exported TF.js model (optional)
- signify-ghana/ — model training & data collection
  - model_training/ — training scripts, export, data analyzer
  - collect/ — simple data collection server (server.py + collection page)
  - samples/ — example JSONL landmark samples
- README.md (this), DEMO_GUIDE.md, VISUAL_SHOWCASE.md

Quick start — prerequisites

- Python 3.10+
- Node 18+ and npm/yarn
- ngrok (optional, for demo/webhook)
- Telegram Bot token (from BotFather)
- Optional: Chrome/Edge for MediaPipe demo

1. Run the Telegram bot (fast demo - polling)

- Install deps:
  ```
  python -m pip install -r wotegslbot/requirements.txt
  ```
- Put BOT token in `wotegslbot/config.py` or environment:
  - PowerShell:
    ```
    $env:BOT_TOKEN="123456:ABC..."
    ```
- Ensure media assets:
  - Add ≥4 distinct files to `wotegslbot/data/videos/words/` (name files by meaning: LAUGH.mp4 or laugh.png)
- Start the bot:
  ```
  cd "c:\Users\HP\Documents\Hackathon\Unicef Startup Lab\codeworks\wotegslbot"
  python bot_enhanced.py
  ```
  Notes:
- For demos use polling mode to avoid webhook/ngrok setup.
- Stop other Telegram clients using the same token (Telegram Desktop/Web) to avoid getUpdates conflicts.

2. Run the web frontend (React, Vite)

- Install & start:
  ```
  cd sign_language
  npm install
  npm run dev
  ```
- Expose to judges:
  ```
  ngrok http 5173
  ```
- If MediaPipe fails on a machine: enable mock detection in `SignDetector.tsx` (UI + game logic remain functional).

3. Optional — Webhook mode for the bot

- Create a small Flask adapter (example in `DEMO_GUIDE.md`) to receive `/webhook`.
- Run Flask on port 5000:
  ```
  python webhook_adapter.py
  ngrok http 5000
  ```
- Set webhook to `https://<ngrok-id>.ngrok.io/webhook`

4. ML pipeline (signify-ghana)

- Collect landmark JSONL samples with `model_training/collect/server.py` (browser-based collection page).
- Train:
  ```
  cd signify-ghana/model_training
  pip install -r requirements.txt
  python train_hybrid_model.py --data ../samples --out model/
  ```
- Export TF.js model:
  - Use the export scripts in `model_training/export_manual.py`
  - Put exported model in `sign_language/public/assets/web_model/` and update model paths in frontend `modelLoader`.

Core implementation & robustness notes

- Case-insensitive exact answer matching (no substring matches).
- Callback parsing robust to underscores in room IDs.
- Active game lifecycle: mark finished + remove game from memory to avoid stale-state "Game not found" errors.
- Bot supports both images and videos; will send photo or video depending on media type.
- Frontend SignDetector supports MediaPipe locateFile fixes and a mock mode for last-minute demos.
- For MediaPipe wasm errors: either pin an older compatible version or use the mock-mode (recommended for quick demos).

Demo checklist (recommended)

- Bot running (polling preferred for demo).
- At least 5 reliable media assets in `wotegslbot/data/videos/words/`.
- Frontend running and exposed via ngrok for live browser demo.
- Two Telegram accounts for 2-player demo OR use solo practice to demo flow.
- Mock detection enabled if MediaPipe unstable.

Common troubleshooting

- "Conflict: terminated by other getUpdates request": close other Telegram clients or processes using same token.
- "Not enough words": ensure folder contains ≥4 distinct supported files.
- MediaPipe runtime (wasm) errors: enable mock mode, pin @mediapipe/hands to known-good version, or use local locateFile path.

Contributing

- Add new media to `wotegslbot/data/videos/words/` named by meaning.
- Improve models or add new exported TF.js model in `sign_language/public/assets/web_model/`.
- Improve labelling or data collection in `signify-ghana/model_training/`.
- Open issues or PRs for features and fixes.

License

- MIT (add LICENSE file if required)

Acknowledgements

- Built for UNICEF Startup Lab — awarded 3rd Place & Best AI Implementation.
- Thanks to contributors, testers, and community sign donors.

Contact

- Open an issue or message the maintainer on Telegram for urgent demo support.

## Presentation & Demo Videos

Below are the presentation and two short demo videos used for the judges. Place the files exactly at the paths shown so GitHub can preview them in the README.

### Presentation (slides)

- PDF: [docs/SignifyGhana_Presentation.pdf](./docs/SignifyGhana_Presentation.pdf)  
  If the PDF isn't present, add it to docs/ or upload to an external host and replace the link.

### Demo — Playthrough (create → join → play → winner)

<details>
<summary>Watch demo_playthrough.mp4 (90–180s)</summary>

<video controls width="720" poster="./demo/thumbnail_playthrough.png">
  <source src="./demo/demo_playthrough.mp4" type="video/mp4">
  Your browser does not support embedded video. Download: [demo/demo_playthrough.mp4](./demo/demo_playthrough.mp4)
</video>

</details>

### Demo — Sign detection (web SignDetector)

<details>
<summary>Watch demo_sign_detection.mp4 (60–90s)</summary>

<video controls width="720" poster="./demo/thumbnail_detection.png">
  <source src="./demo/demo_sign_detection.mp4" type="video/mp4">
  Your browser does not support embedded video. Download: [demo/demo_sign_detection.mp4](./demo/demo_sign_detection.mp4)
</video>

</details>

Notes

- GitHub shows inline players for MP4 files linked this way. If a file is missing the link will 404 — add the file to the indicated folder.
- Recommended: keep each video <50 MB (use ffmpeg to compress) or use Git LFS / external hosting (YouTube unlisted) and replace the src links.
- Optional thumbnails: place poster images at `demo/thumbnail_playthrough.png` and `demo/thumbnail_detection.png` to improve initial render.

How to add files (quick)

```powershell
mkdir docs demo
# copy files into docs/ and demo/
git add docs/SignifyGhana_Presentation.pdf demo/demo_playthrough.mp4 demo/demo_sign_detection.mp4 demo/thumbnail_playthrough.png demo/thumbnail_detection.png
git commit -m "Add presentation and demo videos"
git push
```
