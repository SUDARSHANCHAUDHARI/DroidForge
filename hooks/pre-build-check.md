---
event: PreToolUse
matcher: "Bash"
description: Before running any Bash command that looks like an Android build (gradlew bundleRelease, gradlew assembleRelease), check that the project has a signing config and that the keystore file exists.
---

## Pre-Build Check Hook

This hook fires before Bash tool calls that contain `bundleRelease` or `assembleRelease`.

### Trigger condition

Only activate when the Bash command contains any of:
- `gradlew bundleRelease`
- `./gradlew bundleRelease`
- `gradlew assembleRelease`
- `./gradlew assembleRelease`

If the command does not match, do nothing.

### Checks to perform

1. **Signing config check**: Look for `app/build.gradle.kts`. Check that it contains a `signingConfigs` block with a `release` config. If missing, warn:
   ```
   ⚠  DroidForge: No release signing config found in app/build.gradle.kts
   Run /droidforge:signing-config to generate one.
   ```

2. **Keystore file check**: Read `local.properties` if it exists. Look for `KEYSTORE_PATH`. Check that the referenced `.jks` file exists on disk. If the file is missing, warn:
   ```
   ⚠  DroidForge: Keystore file not found: [path from local.properties]
   Run /droidforge:keystore [AppName] to generate it.
   ```

3. **Version check**: Check that `versionCode` in `app/build.gradle.kts` is an integer ≥ 1. Check that `versionName` is a non-empty string. If either is missing, warn:
   ```
   ⚠  DroidForge: versionCode or versionName missing in build.gradle.kts
   Run /droidforge:version-bump to set them.
   ```

### Behaviour

- These are warnings only — do not block the build command
- Show all applicable warnings at once before the command runs
- If no issues are found, say nothing (do not output an "all clear" message)
