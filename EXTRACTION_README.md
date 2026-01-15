# Claude Export Extraction

This folder was generated from `conversations.json` and contains files reconstructed from Claude "artifacts".

## What was extracted
- Total artifact writes: **160**
- Conversations: **4**
- Manifest: `manifest.csv` lists every extracted artifact with its source message and hash.

## Notes
- If multiple artifacts target the same file path, the **last one in time order wins** (file is overwritten).
- Items that did not look like a file path were saved under `docs/<conversation>/...`.

## Next steps
1. Open the extracted folder and locate `backend/` and `frontend/` directories.
2. Run your usual setup (docker compose / npm install) inside them.
3. If you want, share the extracted zip with your IDE/repo.

Generated at: 2026-01-13T06:33:13.625515Z
