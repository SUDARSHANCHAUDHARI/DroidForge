---
description: Read-only audit of every Android app under a folder — versions, SDK levels, release signing, R8, signing files in git, git state.
argument-hint: "[folder] [--min-target N]"
allowed-tools: Read, Bash
---

Audit every Android app under a folder in one pass. This changes nothing: it reads build files and
asks git for tracked files and status.

## Steps

1. Folder: the first argument in `$ARGUMENTS`, else the current directory.
   Target SDK floor: `--min-target N` from `$ARGUMENTS` if given. Do not invent one: Google raises
   the minimum, so without a number the audit reports targetSdk values and flags nothing for them.
   Mention that the current minimum is shown in Play Console.

2. Run:

   ```bash
   python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/portfolio_audit.py" <folder> [--min-target N]
   ```

   It finds every repo up to three levels down that has `app/build.gradle.kts` or
   `app/build.gradle`, and reports per app: versionName and versionCode, minSdk/targetSdk/compileSdk
   (including `libs.versions` references), AGP and Kotlin from the version catalog, whether the
   release build has a signingConfig and enables R8, signing files tracked by git, a password
   written in the build file, branch and uncommitted changes.

3. Show the table and the issue list exactly as printed. Then, in at most five lines, group the
   issues by what to do first:
   - signing files or passwords in git → rotate and remove first (see the keystore-conventions skill)
   - targetSdk below the floor → plan updates by Play deadline
   - no release signing or no R8 → fix before the next release
   Point to `/droidforge:signing-config`, `/droidforge:gradle-update` or `/droidforge:version-bump`
   where one fits. Do not change any file.
