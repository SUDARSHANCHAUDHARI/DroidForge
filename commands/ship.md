---
description: Take one Android app from code to a signed release bundle — version bump, pre-release checklist, build, and a final summary. Stops for your go at each step and never uploads.
argument-hint: "[patch|minor|major]"
allowed-tools: Read, Write, Bash, AskUserQuestion
---

Ship one Android app: chain the existing DroidForge steps in order, with a stop for the user's go
between each. Nothing is uploaded to Play Console: the result is a signed `.aab` and a summary.

## Config loading

First, read `.claude-plugin-config.json` from the current directory.
- If found: load silently and proceed.
- If not found: stop immediately and output: "Run /droidforge:setup first."

## Steps

1. **Pre-flight (read only).** Run
   `python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/portfolio_audit.py" .` on the current repo and show
   its row. Stop and report if it lists signing files tracked by git, a password in the build file,
   or a release build without a signingConfig: shipping with those is not safe. Otherwise also
   stop if `git status` shows uncommitted changes, and ask whether to continue.

2. **Version.** Follow `/droidforge:version-bump`, using the bump type from `$ARGUMENTS` if given.
   It shows the planned change and waits for confirmation.

3. **Checklist.** Follow `/droidforge:release-checklist`. If any item is marked pending, stop and
   list the pending items; continue only when the user says so.

4. **Build.** Ask for the go, then run `./gradlew bundleRelease`. On failure, show the last 30 lines
   of the error and stop. On success, find the bundle under `app/build/outputs/bundle/release/` and
   report its path and size.

5. **Summary.** Output:

   ```
   SHIP READY — <app>
   ──────────────────
   versionName: <old> → <new> (versionCode <old> → <new>)
   Checklist: <n> done, <n> n/a, 0 pending
   Bundle: <path> (<size>)
   Mapping file: app/build/outputs/mapping/release/mapping.txt (keep it with the release)

   Next, by hand: upload the bundle in Play Console, paste the release notes
   (/playcraft:release-notes if installed), roll out.
   ```

Never commit, tag, push or upload as part of this command. Suggest a commit and tag at the end, and
leave doing it to the user.
