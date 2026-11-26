# handqa — guided human-in-the-loop Android QA harness. Run from this directory.
# FIRERPA_CERT is the lamda.pem from the standalone installer. Never commit it.

set dotenv-load
set shell := ["bash", "-uc"]

FIRERPA_VERSION := env_var_or_default("FIRERPA_VERSION", "10.12")

default:
    @just --list

# Prove the certificate-authenticated gRPC channel and the expected version.
qa-connect:
    cd "{{ justfile_directory() }}" && uv run --python 3.14 handqa connect

# Zero animator duration and enable the UI watcher loop.
qa-prep:
    cd "{{ justfile_directory() }}" && uv run --python 3.14 handqa prep

# Run one YAML suite. The human drives the phone; this process prepares fields and checks output.
# Runs record by default (screen, spoken prompts, and every key/touch as an mp4): tell the person first.
# Add --no-record to turn it off; the start card also offers that (No rec on the bar, norec in the terminal).
# Add --more-coming when another batch follows: the person is then told to wait instead of "use the phone".
qa-run suite *flags:
    cd "{{ justfile_directory() }}" && uv run --python 3.14 handqa run "{{ suite }}" {{ flags }}

# Demonstrate the harness and record every demo trial, even on a previously used device.
qa-demo *flags:
    cd "{{ justfile_directory() }}" && uv run --python 3.14 handqa run suites/harness_demo.yaml --redo {{ flags }}

# A promised batch will not run: tell the person that the phone may be used normally.
qa-release *flags:
    cd "{{ justfile_directory() }}" && uv run --python 3.14 handqa release {{ flags }}

# Print the screen, shade and spoken versions of key tokens, e.g. just qa-keys "<Ctrl+A>, then <Ctrl+C>".
# Live keymap from the phone when ADB_TARGET is set, else the profile.
qa-keys text:
    cd "{{ justfile_directory() }}" && uv run --python 3.14 handqa render {{ quote(text) }}

# Register the proven dialog watchers (no settings change); prints whether each dialog is still showing.
qa-watchers:
    cd "{{ justfile_directory() }}" && uv run --python 3.14 handqa watchers

# Print the foreground app and the screen's nodes; --click RESOURCE_ID clicks first. Debugs "input field not found".
qa-ui *flags:
    cd "{{ justfile_directory() }}" && uv run --python 3.14 handqa ui {{ flags }}

# MCP server on stdio for an agent session.
qa-mcp:
    cd "{{ justfile_directory() }}" && uv run --python 3.14 handqa mcp
