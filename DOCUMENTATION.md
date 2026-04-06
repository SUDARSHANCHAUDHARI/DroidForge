# DroidForge — Full Documentation

This document covers everything needed to use DroidForge effectively. See [README.md](README.md) for a quick overview.

---

## Table of Contents

1. [Installation & Configuration](#installation--configuration)
2. [Commands](#commands)
   - [/droidforge:setup](#droidforgesetup)
   - [/droidforge:new-app](#droidforgenew-app)
   - [/droidforge:keystore](#droidforgekeystore)
   - [/droidforge:signing-config](#droidforgesigning-config)
   - [/droidforge:version-bump](#droidforgeversion-bump)
   - [/droidforge:gradle-update](#droidforgegradle-update)
   - [/droidforge:release-checklist](#droidforgerelease-checklist)
3. [Agents](#agents)
4. [Skills](#skills)
5. [Hooks](#hooks)
6. [Gradle Compatibility Matrix](#gradle-compatibility-matrix)
7. [Config File Reference](#config-file-reference)
8. [Troubleshooting](#troubleshooting)
9. [Plugin Architecture](#plugin-architecture)

---

## Installation & Configuration

### Install the plugin

```bash
/plugin install droidforge
```

### First-time setup

Run once per project (or in your workspace root to use across all projects):

```
/droidforge:setup
```

This creates `.claude-plugin-config.json` in the current directory and automatically adds it to `.gitignore`. It is never committed.

### Config fields saved by setup

| Field | Description | Example |
|---|---|---|
| `developer.name` | Your full name or display name | `Jane Smith` |
| `developer.company` | Developer label shown in keystores | `JaneTechLabs` |
| `developer.github_username` | GitHub username | `janecoder` |
| `developer.country` | Country of operation | `United States` |
| `developer.country_code` | 2-letter ISO code for keystore | `US` |
| `developer.city` | City for keystore dname | `New York` |
| `android.package_prefix` | Prefix for all your apps | `com.janecoder` |
| `android.keystore_password` | Keystore password (stored locally only) | `YourPassword` |
| `github_pages.privacy_policy_pattern` | Privacy policy URL template | `https://janecoder.github.io/{appname}-privacy-policy/` |

---

## Commands

### /droidforge:setup

Run once per project. Saves your developer conventions locally.

- Creates `.claude-plugin-config.json`
- Adds it to `.gitignore`
- If config already exists, shows current values and asks before overwriting

**Example output:**
```
DROIDFORGE SETUP COMPLETE
──────────────────────────
Developer:      Jane Smith (JaneTechLabs)
GitHub:         janecoder
Package prefix: com.janecoder
Keystore pass:  ••••••••• (saved locally)
Country:        United States (US)
City:           New York

All DroidForge commands will now use these settings.
IMPORTANT: .claude-plugin-config.json is in your .gitignore — never commit it.
```

---

### /droidforge:new-app

Scaffold a complete new Android app.

**Asks for:** App name, category/purpose, minSdk, targetSdk, AdMob (y/n), IAP (y/n)

**Generates:**
- `app/build.gradle.kts` — with namespace, signingConfigs, buildTypes, dependencies
- `gradle/libs.versions.toml` — full version catalog with current stable versions
- `app/src/main/AndroidManifest.xml`
- `app/src/main/java/.../MainActivity.kt`
- `proguard-rules.pro`
- `.gitignore`

**Derived automatically:**
- Package name: `{config.android.package_prefix}.[appname_lowercase]`
- Privacy policy URL: `{config.github_pages.privacy_policy_pattern}`

**Example output:**
```
NEW APP SCAFFOLDED
──────────────────
App name:       TaskMaster
Package:        com.janecoder.taskmaster
Min SDK:        24
Target SDK:     35
Keystore:       taskmaster.jks (alias: taskmaster)
Privacy policy: https://janecoder.github.io/taskmaster-privacy-policy/

Files created:
  app/build.gradle.kts
  gradle/libs.versions.toml
  app/src/main/AndroidManifest.xml
  app/src/main/java/com/janecoder/taskmaster/MainActivity.kt
  proguard-rules.pro
  .gitignore

NEXT STEPS:
1. Add local.properties entries shown above (never commit this file)
2. Run: ./gradlew sync
3. Verify the app builds before adding features
```

---

### /droidforge:keystore

Generate a keystore for an Android app.

**Always shows the full `keytool` command before running. Never executes without explicit user confirmation.**

```bash
keytool -genkeypair \
  -alias taskmaster \
  -keypass yourpassword \
  -storepass yourpassword \
  -keystore taskmaster.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -dname "CN=JaneTechLabs, OU=Mobile, O=JaneTechLabs, L=New York, ST=New York, C=US"
```

After creation, verifies with `keytool -list -v` and outputs the signing config block.

**Example output:**
```
KEYSTORE CREATED: taskmaster.jks
──────────────────────────────────────────
⚠  Add *.jks to .gitignore — never commit keystores
⚠  Back up this file to secure cloud storage immediately
⚠  Losing this keystore = cannot update the app on Play Store
✓  Keystore password matches your DroidForge config
✓  Validity: 10000 days (~27 years)
```

---

### /droidforge:signing-config

Generate the signing configuration block for `app/build.gradle.kts`.

**Recommended approach** (using `local.properties`):
```kotlin
import java.util.Properties

val localProps = Properties().apply {
    file("../local.properties").takeIf { it.exists() }?.inputStream()?.use { load(it) }
}

android {
    signingConfigs {
        create("release") {
            storeFile = file(localProps["KEYSTORE_PATH"] as? String ?: "")
            storePassword = localProps["KEYSTORE_PASSWORD"] as? String ?: ""
            keyAlias = localProps["KEY_ALIAS"] as? String ?: ""
            keyPassword = localProps["KEY_PASSWORD"] as? String ?: ""
        }
    }
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

**local.properties entries to add manually (never commit this file):**
```properties
KEYSTORE_PATH=taskmaster.jks
KEYSTORE_PASSWORD=yourpassword
KEY_ALIAS=taskmaster
KEY_PASSWORD=yourpassword
```

**Example output:**
```
SIGNING CONFIG GENERATED
────────────────────────
✓  local.properties is excluded from git by Android Studio's default .gitignore
✓  Verify .gitignore includes: local.properties and *.jks
✓  Run ./gradlew signingReport to verify signing is configured correctly
```

---

### /droidforge:version-bump

Bump `versionCode` and `versionName` in `app/build.gradle.kts`.

| Bump type | Example | When to use |
|---|---|---|
| patch | 1.2.3 → 1.2.4 | Bug fix release |
| minor | 1.2.3 → 1.3.0 | New feature release |
| major | 1.2.3 → 2.0.0 | Breaking change / major update |

`versionCode` always increments by exactly 1 (Play Store requirement). Shows preview before editing. Optionally creates a git tag.

**Example output:**
```
VERSION BUMP PREVIEW
────────────────────
versionCode:  12 → 13
versionName:  "1.2.3" → "1.2.4"

Proceed? (y/n)

VERSION BUMP COMPLETE
─────────────────────
versionCode:  12 → 13
versionName:  "1.2.3" → "1.2.4"

Create a git tag for this version? (y/n)
```

---

### /droidforge:gradle-update

Update `gradle/libs.versions.toml` with latest stable versions.

**Compatibility checks performed:**
- AGP version ↔ Gradle wrapper version
- Kotlin version ↔ Compose compiler (uses plugin alias for Kotlin 2.0+)
- `compileSdk` ≥ `targetSdk`
- Only stable releases — no alpha/beta/RC

Shows a full diff before writing. Does not modify files until confirmed.

**Example output:**
```
DEPENDENCY UPDATES
──────────────────
agp:                8.4.0  → 8.7.0
kotlin:             2.0.0  → 2.1.0
coreKtx:            1.13.1 → 1.15.0
lifecycleRuntimeKtx: 2.8.2 → 2.8.7
activityCompose:    1.9.0  → 1.10.0
composeBom:         2024.06.00 → 2025.02.00

NO CHANGE:
junit:              4.13.2 (already current)
espressoCore:       3.6.1  (already current)

COMPATIBILITY NOTES:
- AGP 8.7.0 requires Gradle wrapper 8.9+ — update gradle-wrapper.properties
- Kotlin 2.1.0: continue using alias(libs.plugins.kotlin.compose) ✓

Proceed with these updates? (y/n)

GRADLE UPDATE COMPLETE
──────────────────────
✓  libs.versions.toml updated
→  Run ./gradlew sync to apply changes
→  Update gradle/wrapper/gradle-wrapper.properties to distributionUrl with Gradle 8.9+
```

---

### /droidforge:release-checklist

Interactive pre-submission checklist with 5 sections.

**Example output:**
```
RELEASE CHECKLIST — TaskMaster
───────────────────────────────
Current version: 1.2.4 (code: 13)

SECTION 1 — BUILD
✓  versionCode incremented (13)
✓  versionName updated (1.2.4)
…  Release AAB built with release signing config — pending
✓  ProGuard/R8 enabled
✓  Build passes without errors

SECTION 2 — TESTING
✓  Tested on physical device
✓  Tested on Android 7+
✓  Crash-free on core user flows
✓  No debug features visible

SECTION 3 — PLAY CONSOLE
✓  Store listing up to date
✓  Screenshots current
✓  Release notes written
…  Data safety section — pending
✓  Content rating current

SECTION 4 — APP CONTENT
✓  Privacy policy live: https://janecoder.github.io/taskmaster-privacy-policy/
✓  Permissions match manifest
✓  No unused permissions

SECTION 5 — POST-SUBMISSION
✓  Git tag created: v1.2.4
✓  Release notes committed
…  App tracker updated — pending

RELEASE CHECKLIST COMPLETE
───────────────────────────
✓  Done:    12
…  Pending: 3
─  N/A:     0

⚠  Resolve pending items before submitting to Play Store.
```

---

## Agents

### setup-agent

Scaffolds complete, production-ready Android projects. Triggered when user asks to create a new Android app or generate project files.

**Triggered by phrases like:**
- "Create a new Android app called..."
- "Scaffold an Android project for..."
- "Set up a new app with package..."

### gradle-agent

Gradle and version catalog expert. Triggered on Gradle dependency questions, build failures, or version catalog updates. Enforces Kotlin 2.0+ Compose plugin pattern and AGP/Gradle compatibility rules.

**Triggered by phrases like:**
- "Update my Gradle dependencies..."
- "My build is failing with a Compose compiler error..."
- "Set up libs.versions.toml for my project..."

### release-agent

Handles version bumps, changelog generation from git log, and annotated git tagging. Always shows commands and asks for confirmation before `git tag` or `git push`.

**Triggered by phrases like:**
- "I'm ready to release version 2.1.0..."
- "Generate release notes from my git history..."
- "Create a git tag for my release..."

---

## Skills

Skills are loaded automatically by Claude when relevant context is detected.

| Skill | Trigger | What it provides |
|---|---|---|
| `keystore-conventions` | Creating keystores or configuring signing | RSA 2048 params, keytool command format, Play App Signing guide |
| `package-naming` | Creating new apps or setting up package names | Naming rules, privacy policy URL pattern, repo naming |
| `gradle-best-practices` | Editing build.gradle.kts or libs.versions.toml | Kotlin DSL rules, Kotlin 2.0+ Compose plugin setup, ProGuard config |
| `multi-app-structure` | Working across multiple apps or managing a portfolio | Repo strategy, shared code, keystore management, triage priority |
| `release-workflow` | Preparing a release or building a signed AAB | Pre-release steps, build commands, staged rollout strategy |

---

## Hooks

### pre-build-check (PreToolUse)

Fires before any Bash call containing `gradlew bundleRelease` or `gradlew assembleRelease`. Checks:
- `signingConfigs` block exists in `build.gradle.kts`
- Keystore file referenced in `local.properties` exists on disk
- `versionCode` and `versionName` are present

Warnings only — does not block the build.

**Example warning:**
```
⚠  DroidForge: Keystore file not found: taskmaster.jks
   Run /droidforge:keystore TaskMaster to generate it.
```

### post-version-bump (PostToolUse)

Fires after any Write call to `build.gradle.kts` that changes `versionCode` or `versionName`. Reminds the user to update `CHANGELOG.md` and create a git tag.

**Example reminder:**
```
DroidForge: Version updated in build.gradle.kts

Suggested next steps:
  1. Update CHANGELOG.md with changes in this version
  2. Create a git tag:  git tag -a v1.2.4 -m "Release 1.2.4"
  3. Run the release checklist:  /droidforge:release-checklist
```

---

## Gradle Compatibility Matrix

Use this table when updating AGP, Kotlin, or Gradle wrapper versions.

### AGP ↔ Gradle Wrapper

| AGP Version | Min Gradle Version | Recommended |
|---|---|---|
| 8.7.x | 8.9+ | 8.10 |
| 8.6.x | 8.7+ | 8.8 |
| 8.5.x | 8.7+ | 8.7 |
| 8.4.x | 8.6+ | 8.6 |
| 8.3.x | 8.4+ | 8.5 |
| 8.2.x | 8.2+ | 8.3 |

Update `gradle/wrapper/gradle-wrapper.properties`:
```properties
distributionUrl=https\://services.gradle.org/distributions/gradle-8.10-bin.zip
```

### Kotlin ↔ Compose Compiler

| Kotlin Version | Compose Approach | Notes |
|---|---|---|
| 2.1.x | `alias(libs.plugins.kotlin.compose)` | Use Compose compiler Gradle plugin |
| 2.0.x | `alias(libs.plugins.kotlin.compose)` | Use Compose compiler Gradle plugin |
| 1.9.x | `kotlinCompilerExtensionVersion = "1.5.x"` | Legacy approach — upgrade recommended |
| 1.8.x | `kotlinCompilerExtensionVersion = "1.4.x"` | No longer supported |

For Kotlin 2.0+, add to `libs.versions.toml`:
```toml
[plugins]
kotlin-compose = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
```

And to `app/build.gradle.kts`:
```kotlin
plugins {
    alias(libs.plugins.kotlin.compose)
}
```

### compileSdk / targetSdk / minSdk

| Field | Recommended | Notes |
|---|---|---|
| `compileSdk` | 35 | Must be ≥ targetSdk |
| `targetSdk` | 35 | Play Store requires 35 for new submissions (as of 2024) |
| `minSdk` | 24 | Android 7.0 — ~96% device coverage |

### Current Stable Versions (April 2026)

| Dependency | Version |
|---|---|
| AGP | 8.7.0 |
| Kotlin | 2.1.0 |
| Compose BOM | 2025.02.00 |
| Core KTX | 1.15.0 |
| Lifecycle Runtime KTX | 2.8.7 |
| Activity Compose | 1.10.0 |
| JUnit | 4.13.2 |
| Espresso | 3.6.1 |

> Always verify against [Google Maven](https://maven.google.com) and [Maven Central](https://search.maven.org) for the latest stable releases.

---

## Config File Reference

`.claude-plugin-config.json` (local only, never committed):

```json
{
  "developer": {
    "name": "Your Name",
    "company": "YourCompany",
    "github_username": "yourhandle",
    "country": "Your Country",
    "country_code": "US",
    "city": "Your City"
  },
  "android": {
    "package_prefix": "com.yourcompany",
    "keystore_password": "••••••••",
    "keystore_cn": "YourCompany",
    "keystore_country_code": "US",
    "keystore_city": "Your City"
  },
  "github_pages": {
    "privacy_policy_pattern": "https://yourhandle.github.io/{appname}-privacy-policy/"
  },
  "plugin_version": "1.0.0",
  "configured_at": "2026-04-06"
}
```

This file is created by `/droidforge:setup` and automatically excluded from git. All commands read from it silently — if it is missing, every command stops and asks you to run `/droidforge:setup` first.

---

## Troubleshooting

### "Run /droidforge:setup first"

Every command checks for `.claude-plugin-config.json` in the current directory. If you see this message:

1. Make sure you are in the right project directory
2. Run `/droidforge:setup` to create the config

### `keytool: command not found`

`keytool` is part of the Java JDK. Fix:

1. Install a JDK if you haven't: [adoptium.net](https://adoptium.net) or Android Studio bundles one
2. Add it to your PATH:
   ```bash
   # macOS — add to ~/.zshrc or ~/.bash_profile
   export JAVA_HOME=$(/usr/libexec/java_home)
   export PATH=$JAVA_HOME/bin:$PATH
   ```
3. Verify: `keytool -help`

On macOS you can also use the JDK bundled with Android Studio:
```bash
export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
```

### Signing config not working — `ClassCastException` at Gradle sync

This happens if `local.properties` is missing one of the required keys. Check that all four are present:
```properties
KEYSTORE_PATH=yourapp.jks
KEYSTORE_PASSWORD=yourpassword
KEY_ALIAS=yourapp
KEY_PASSWORD=yourpassword
```

### `./gradlew bundleRelease` — wrong signing key

Run `./gradlew signingReport` to confirm which keystore and alias are being used for the release build. If it shows `debugAndroidTest` or `debug`, the `signingConfig` is not wired to the release buildType.

### AGP / Gradle version mismatch at sync

Update `gradle/wrapper/gradle-wrapper.properties` to a Gradle version compatible with your AGP. See [Gradle Compatibility Matrix](#gradle-compatibility-matrix) above.

---

## Plugin Architecture

```
droidforge/
├── .claude-plugin/
│   ├── plugin.json              # Plugin manifest, commands, agents, skills, hooks
│   └── marketplace.json         # Marketplace listing metadata
├── commands/
│   ├── setup.md                 # /droidforge:setup
│   ├── new-app.md               # /droidforge:new-app
│   ├── keystore.md              # /droidforge:keystore
│   ├── signing-config.md        # /droidforge:signing-config
│   ├── version-bump.md          # /droidforge:version-bump
│   ├── gradle-update.md         # /droidforge:gradle-update
│   └── release-checklist.md     # /droidforge:release-checklist
├── agents/
│   ├── setup-agent.md           # Scaffolds complete Android projects
│   ├── gradle-agent.md          # Gradle/version catalog expert
│   └── release-agent.md         # Version bump, changelog, git tagging
├── skills/
│   ├── keystore-conventions/    # Keystore parameters, Play App Signing
│   ├── package-naming/          # Package name rules, privacy policy URL pattern
│   ├── gradle-best-practices/   # Kotlin DSL, version catalog, Compose setup
│   ├── multi-app-structure/     # Portfolio management, repo strategy
│   └── release-workflow/        # End-to-end release process
├── hooks/
│   ├── pre-build-check.md       # PreToolUse — warns before release builds
│   └── post-version-bump.md     # PostToolUse — reminds after version changes
├── CHANGELOG.md
├── DOCUMENTATION.md             # This file
├── LICENSE
└── README.md
```

### How commands, agents, and skills interact

- **Commands** (`commands/*.md`) — define the user-facing workflow step by step. They load config, ask questions, and execute tasks directly or by invoking agents.
- **Agents** (`agents/*.md`) — autonomous specialists triggered automatically by context or explicitly invoked by the user. Each agent has a focused responsibility.
- **Skills** (`skills/*/SKILL.md`) — reference knowledge loaded automatically by Claude when the context matches. They carry the detailed rules and tables that commands and agents rely on, without bloating the command files themselves.
- **Hooks** (`hooks/*.md`) — event-driven checks that fire automatically on specific tool calls. They add passive safety without requiring user action.
