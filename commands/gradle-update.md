---
description: Update dependencies in an Android project's Gradle version catalog (libs.versions.toml).
argument-hint: "[all|kotlin|agp|compose|<library-name>]"
allowed-tools: Read, Write, AskUserQuestion
---

Update dependencies in an Android project's Gradle version catalog (`gradle/libs.versions.toml`).

## Config loading

First, read `.claude-plugin-config.json` from the current directory.
- If found: load silently and proceed.
- If not found: stop immediately and output: "Run /droidforge:setup first."

## Steps

1. Read `gradle/libs.versions.toml`. If not found, check `libs.versions.toml` in the project root. If still not found, ask the user for the path.

2. If no argument was provided, ask which area to update:
   ```
   What would you like to update?
   1. All dependencies
   2. Kotlin / AGP / Compose versions only
   3. A specific library (provide name)
   ```

3. For each dependency being updated, determine the latest stable version:
   - Use your training knowledge of current stable versions (as of 2025–2026)
   - For libraries where you are uncertain of the exact latest version, note them with "verify on Maven Central" rather than guessing
   - Never suggest alpha, beta, or RC versions unless the user explicitly asks

4. Check for known compatibility constraints before suggesting updates:
   - Kotlin version must be compatible with the AGP version
   - Kotlin 2.0+ requires `kotlin-compose` compiler plugin (not `kotlinCompilerExtensionVersion`)
   - AGP version determines the minimum required Gradle wrapper version:
     - AGP 8.4.x → Gradle 8.6+
     - AGP 8.3.x → Gradle 8.4+
   - `compileSdk` must be ≥ `targetSdk`
   - `targetSdk` for new Play Store submissions should be the latest stable API level (35 as of 2025)

5. Generate the updated version entries. Do NOT write to disk yet.

6. Show a diff of what will change:
   ```
   DEPENDENCY UPDATES
   ──────────────────
   kotlin:        [old] → [new]
   agp:           [old] → [new]
   composeBom:    [old] → [new]
   coreKtx:       [old] → [new]
   ...

   NO CHANGE:
   junit:         [version] (already current)
   ...

   COMPATIBILITY NOTES:
   - [any relevant warnings about version interactions]
   - [any manual steps required, e.g. gradle-wrapper.properties update]

   Proceed with these updates? (y/n)
   ```

7. On confirmation, write the updated `gradle/libs.versions.toml` to disk.

8. Remind user:
   ```
   GRADLE UPDATE COMPLETE
   ──────────────────────
   ✓  libs.versions.toml updated
   → Run ./gradlew sync to apply changes
   → Fix any build errors from API changes before committing
   → Check COMPATIBILITY NOTES above for any manual steps
   ```
