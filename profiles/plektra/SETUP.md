# Set up guided Android QA for Plektra (`handqa`)

Watch the [2:03 Titan 2 Elite demo video](../../media/plektra-harness-demo.mp4) to see a full recorded run (movable bar, QA bubble, redo, software-keyboard toggle, field focus, key/touch overlay, and spoken prompts).

## Paste this prompt into your AI coding agent

Paste the block below into an AI coding agent working inside **any Plektra checkout or branch** (upstream `main`, a feature branch, or a fork). It installs the project-agnostic [`handqa`](https://github.com/frdminc/handqa) harness alongside your checkout (keeping your Plektra git tree clean) and wires up the Plektra-specific profile.

```text
Set up the complete guided human-in-the-loop Android QA system (handqa + Plektra profile) for the Plektra branch I am currently working on, without polluting my Plektra git checkout.

1. Clone handqa outside this Plektra repo (e.g. `../handqa` from `https://github.com/frdminc/handqa.git`, branch `main`). Confirm `../handqa/Justfile` and `../handqa/suites/harness_demo.yaml` exist.

2. Check host tools: `uv`, `just`, and `adb`, plus `scrcpy` and `ffmpeg` for default video recording. Install anything missing using the host's package manager. Optionally set up offline narration (`uv tool install --python 3.13 kokoro-cli && kokoro setup && kokoro doctor`); otherwise `handqa` falls back to macOS `say` or Linux `espeak`.

3. Pick my authorized Android developer phone from `adb devices -l` (ask me if more than one device is listed, and pass `-s <target>` to every device-changing adb command). Verify that the selected IME belongs to the debuggable Plektra build I intend to test:
   - Check `adb -s <target> shell settings get secure default_input_method` to identify the active Plektra package (e.g. `rocks.pkb.plektra` or a fork ID).
   - Verify `adb -s <target> shell run-as <package> id` succeeds (debuggable build required for reading keymap prefs and toggling software-keyboard mode).
   - If a debug build from my current Plektra branch needs to be built and installed first, use this checkout's documented build/install route. Stop and report to me on any signature mismatch.

4. Set up the phone companion tools:
   - Reuse a working FIRERPA 10.12 setup if already present; otherwise follow `../handqa/docs/firerpa-hitl.md` section 1 to install non-root FIRERPA 10.12 over adb and keep `lamda.pem` outside every git repository.
   - Download the latest `hitl-button-bar-*.apk` (version 0.4.1 / versionCode 5 or later) and its `.sha256` checksum from `https://github.com/frdminc/handqa/releases` (or build locally with `gradle -p ../handqa/overlay-app assembleDebug`). Verify the checksum, install with `adb -s <target> install -r`, and grant draw-over-apps permission (`adb -s <target> shell appops set dev.hitlbar.overlay SYSTEM_ALERT_WINDOW allow`).

5. Configure `../handqa/.env` (copy from `../handqa/.env.example`, `chmod 600 ../handqa/.env`, never commit):
   - Set `FIRERPA_HOST`, `FIRERPA_PORT`, `FIRERPA_CERT` (path to `lamda.pem`), and `FIRERPA_VERSION=10.12`.
   - Set `ADB_TARGET=<resolved adb transport>`.
   - Set `HANDQA_PROFILE=plektra` and `HANDQA_PACKAGE=<active debuggable Plektra package>`.
   - If I am testing on a Unihertz Titan 2 Elite, set `HANDQA_KEYMAP=profiles/plektra/keymaps/titan2-elite-baseline.yaml`.
   - Verify connectivity with `just --justfile ../handqa/Justfile qa-connect` and report readiness once FIRERPA, the debuggable Plektra IME, and the overlay APK checks all pass.

6. Wait until I tell you I am holding the phone, then run the 7-trial synthetic bench smoke test:
   - Tell me that `handqa` records the screen, spoken prompts, keys, and touches by default, and offer the opt-out (`No rec` on the phone start card or `--no-record`).
   - Never bypass a lock screen, never clear or send pre-existing drafts, and never start a batch without waiting at the start card.
   - Run `just --justfile ../handqa/Justfile qa-demo` (uses only the built-in test bench and synthetic text; software-keyboard switching works on upstream Plektra `main` out of the box via `KeyboardBarTestReceiver`).
   - Confirm all 7 trials pass, verify the end-of-batch handback announcement, and report the MP4 path (if recorded).

7. After the smoke test passes, tell me we are ready to run Plektra suites (`../handqa/profiles/plektra/suites/`), write a YAML suite for my current branch, or connect `just --justfile ../handqa/Justfile qa-mcp` as an MCP server.
```

## What this sets up

1. **Generic harness (`handqa`):** spoken prompts, movable translucent button bar + QA bubble (`dev.hitlbar.overlay` `0.4.1+`), built-in 9-box typing bench with `QAPROBE` event diagnostics, synchronized screen/voice/key/touch recording, phone-side stop/rollback safety, and stdio MCP server ([main README](../../README.md)).
2. **Plektra profile (`profiles/plektra/`):**
   1. Live `key-remap-v2` preference reader (`shared_prefs/plektra_prefs.xml`) so keycap instructions reflect your active Plektra remaps.
   2. Software-keyboard mode toggle + phone-side rollback via Plektra's `SoftwareKeyboardModeActionActivity` and `KeyboardBarTestReceiver` (already present on upstream `pkb-rocks/plektra` `main`).
   3. Reference Titan 2 Elite keymap ([titan2-elite-baseline.yaml](keymaps/titan2-elite-baseline.yaml)), device facts ([titan2-elite-facts.md](titan2-elite-facts.md)), and Plektra suites ([smoke_chords.yaml](suites/smoke_chords.yaml), [tab_first_letter.yaml](suites/tab_first_letter.yaml)).
3. **Links:**
   1. [2:03 demo video](../../media/plektra-harness-demo.mp4)
   2. [Overlay APK releases](https://github.com/frdminc/handqa/releases) · [Overlay app README](../../overlay-app/README.md)
   3. [FIRERPA non-root setup](../../docs/firerpa-hitl.md#1-install-and-configure-the-users-device-over-adb)
   4. [Plektra upstream automated input flows](https://github.com/pkb-rocks/plektra/blob/main/docs/testing/input-flows.md) (for headless/injected replay; use `handqa` when real physical keys, gestures, or human observation are needed)
