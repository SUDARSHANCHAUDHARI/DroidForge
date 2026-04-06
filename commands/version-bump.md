---
description: Bump versionCode and versionName in an Android app's build.gradle.kts.
argument-hint: "[patch|minor|major]"
allowed-tools: Read, Write, Bash, AskUserQuestion
---

Bump the `versionCode` and `versionName` in an Android app's `build.gradle.kts`.

## Config loading

First, read `.claude-plugin-config.json` from the current directory.
- If found: load silently and proceed.
- If not found: stop immediately and output: "Run /droidforge:setup first."

## Steps

1. Find `app/build.gradle.kts`. If not found, ask the user for the path to the build file.

2. Read the file and extract:
   - Current `versionCode` (integer)
   - Current `versionName` (string, e.g. "1.2.3")
   If either cannot be found, report the error and stop.

3. If a bump type was provided as an argument, use it. Otherwise ask:
   ```
   What type of version bump?
   1. patch — bug fix release (e.g. 1.2.3 → 1.2.4)
   2. minor — new feature release (e.g. 1.2.3 → 1.3.0)
   3. major — breaking change / major update (e.g. 1.2.3 → 2.0.0)
   ```

4. Calculate new values:
   - `versionCode`: always increment by exactly 1 (required by Play Store)
   - `versionName`: parse as `MAJOR.MINOR.PATCH` and apply:
     - patch → increment PATCH, keep MAJOR.MINOR
     - minor → increment MINOR, reset PATCH to 0, keep MAJOR
     - major → increment MAJOR, reset MINOR and PATCH to 0
   - If versionName is not in `X.Y.Z` format, ask user what the new versionName should be

5. Show the planned change and ask for confirmation:
   ```
   VERSION BUMP PREVIEW
   ────────────────────
   versionCode:  [current] → [new]
   versionName:  "[current]" → "[new]"

   Proceed? (y/n)
   ```

6. On confirmation, edit `app/build.gradle.kts` using exact string replacement:
   - Replace `versionCode = [old]` with `versionCode = [new]`
   - Replace `versionName = "[old]"` with `versionName = "[new]"`

7. Confirm the update:
   ```
   VERSION BUMP COMPLETE
   ─────────────────────
   versionCode:  [old] → [new]
   versionName:  "[old]" → "[new]"
   ```

8. Ask: "Create a git tag for this version? (y/n)"
   - If y: show the command and ask for confirmation before running:
     ```bash
     git tag -a v[new_versionName] -m "Release [new_versionName]"
     ```
   - After user confirms, run it, then ask: "Push this tag to origin? (y/n)"
   - If y: run `git push origin v[new_versionName]`
