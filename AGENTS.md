# Agent instructions for handqa

`handqa` is a project-agnostic guided human-in-the-loop (HITL) QA harness for Android devices, with an accompanying Android overlay app (`overlay-app/`, package `dev.hitlbar.overlay`) and optional project profiles under `profiles/` (such as `profiles/plektra/`).

## Rules

1. **Human-in-the-loop safety:** Never start a guided phone batch without waiting for the human's explicit start (`StartGate`). Never bypass a lock screen, never clear or send pre-existing drafts, and always restore phone settings + announce end-of-batch state (`EndNotice`: either "wait, another batch is coming" or "done, the phone may be used normally").
2. **Recording:** Runs record by default (screen, spoken prompts, key/touch overlay, chapters). Always tell the operator before starting a run and offer the `--no-record` / `No rec` opt-out.
3. **Overlay app builds:** Build and test `overlay-app/` on GitHub Actions (`.github/workflows/ci.yml` and `.github/workflows/release-overlay.yml`), not via local Gradle on constrained hosts.
4. **Tests:** Run the Python unit tests (`uv run --locked --group dev pytest -q`) before pushing changes to `handqa/`.
5. **Secrets and device config:** Never commit `.env`, `lamda.pem`, device IPs, or serials. Keep all machine-local config in gitignored `.env` or environment variables.
