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
6. [Config File Reference](#config-file-reference)
7. [Plugin Architecture](#plugin-architecture)

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

---

### /droidforge:keystore

Generate a keystore for an Android app.

**Always shows the full `keytool` command before running. Never executes without explicit user confirmation.**

```bash
keytool -genkeypair \
  -alias [appname_lowercase] \
  -keypass [password] \
  -storepass [password] \
  -keystore [appname_lowercase].jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -dname "CN=[company], OU=Mobile, O=[company], L=[city], ST=[city], C=[country_code]"
```

After creation, verifies with `keytool -list -v` and outputs the signing config block.

---

### /droidforge:signing-config

Generate the signing configuration block for `app/build.gradle.kts`.

**Recommended approach** (using `local.properties`):
```kotlin
val localProps = Properties().apply {
    file("../local.properties").takeIf { it.exists() }?.inputStream()?.use { load(it) }
}
signingConfigs {
    create("release") {
        storeFile = file(localProps["KEYSTORE_PATH"] as String)
        storePassword = localProps["KEYSTORE_PASSWORD"] as String
        keyAlias = localProps["KEY_ALIAS"] as String
        keyPassword = localProps["KEY_PASSWORD"] as String
    }
}
```

---

### /droidforge:version-bump

Bump `versionCode` and `versionName` in `app/build.gradle.kts`.

| Bump type | Example |
|---|---|
| patch | 1.2.3 → 1.2.4 |
| minor | 1.2.3 → 1.3.0 |
| major | 1.2.3 → 2.0.0 |

`versionCode` always increments by exactly 1 (Play Store requirement). Shows preview before editing. Optionally creates a git tag.

---

### /droidforge:gradle-update

Update `gradle/libs.versions.toml` with latest stable versions.

**Compatibility checks performed:**
- AGP version ↔ Gradle wrapper version
- Kotlin version ↔ Compose compiler (uses plugin alias for Kotlin 2.0+)
- `compileSdk` ≥ `targetSdk`
- Only stable releases — no alpha/beta/RC

Shows a full diff before writing. Does not modify files until confirmed.

---

### /droidforge:release-checklist

Interactive pre-submission checklist with 5 sections:

1. **Build** — versionCode, versionName, AAB signed with release config, ProGuard enabled
2. **Testing** — physical device, Android 7+ compliance, no debug features
3. **Play Console** — store listing, screenshots, release notes, data safety, content rating
4. **App Content** — privacy policy live, permissions match manifest
5. **Post-Submission** — git tag, changelog committed, app tracker updated

---

## Agents

### setup-agent

Scaffolds complete, production-ready Android projects. Triggered when user asks to create a new Android app or generate project files.

### gradle-agent

Gradle and version catalog expert. Triggered on Gradle dependency questions, build failures, or version catalog updates. Enforces Kotlin 2.0+ Compose plugin pattern and AGP/Gradle compatibility rules.

### release-agent

Handles version bumps, changelog generation from git log, and annotated git tagging. Always shows commands and asks for confirmation before `git tag` or `git push`.

---

## Skills

Skills are loaded automatically by Claude when relevant context is detected.

| Skill | Trigger |
|---|---|
| `keystore-conventions` | Creating keystores or configuring signing |
| `package-naming` | Creating new apps or setting up package names |
| `gradle-best-practices` | Editing build.gradle.kts or libs.versions.toml |
| `multi-app-structure` | Working across multiple apps or managing a portfolio |
| `release-workflow` | Preparing a release or building a signed AAB |

---

## Hooks

### pre-build-check (PreToolUse)

Fires before any Bash call containing `gradlew bundleRelease` or `gradlew assembleRelease`. Checks:
- `signingConfigs` block exists in `build.gradle.kts`
- Keystore file referenced in `local.properties` exists on disk
- `versionCode` and `versionName` are present

Warnings only — does not block the build.

### post-version-bump (PostToolUse)

Fires after any Write call to `build.gradle.kts` that changes `versionCode` or `versionName`. Reminds the user to update `CHANGELOG.md` and create a git tag.

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
    "keystore_password": "yourpassword",
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

---

## Plugin Architecture

```
droidforge/
├── .claude-plugin/
│   ├── plugin.json          — plugin manifest
│   └── marketplace.json     — marketplace listing metadata
├── commands/                — 7 slash commands
├── agents/                  — 3 autonomous agents
├── skills/
│   └── <name>/SKILL.md      — 5 auto-loaded knowledge skills
├── hooks/                   — 2 event-driven hooks
├── CHANGELOG.md
├── DOCUMENTATION.md
├── LICENSE
└── README.md
```

All user data flows through `.claude-plugin-config.json` — created by `/droidforge:setup`, stored locally, never committed.
