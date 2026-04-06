# DroidForge — Claude Code Plugin

> Automate every repetitive Android dev task — keystore creation, signing config, version bumping, Gradle version catalog management, new app scaffolding, and release checklists.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Claude%20Code-blueviolet)
![Target](https://img.shields.io/badge/target-Android%20%2F%20Google%20Play-brightgreen)

---

## What It Does

1. Run `/droidforge:setup` once — saves your developer conventions locally per project
2. Scaffold a complete new Android app with correct package names, signing config, and version catalog
3. Generate keystores with consistent conventions — shows the `keytool` command, asks before running
4. Bump `versionCode` and `versionName` with semver (patch / minor / major)
5. Update `libs.versions.toml` with compatibility checks (AGP ↔ Gradle ↔ Kotlin ↔ Compose)
6. Run an interactive pre-submission checklist before every Play Store release

---

## Install

```bash
/plugin install droidforge
```

Run `/droidforge:setup` once per project to save your conventions. All other commands use your saved config automatically — no repeated questions, no hardcoded values.

---

## Quick Start

**1. Set up your conventions**
```
/droidforge:setup
```
Saves your developer name, package prefix, keystore password, and GitHub info to `.claude-plugin-config.json` (auto-added to `.gitignore`).

**2. Scaffold a new app**
```
/droidforge:new-app
```
Generates `app/build.gradle.kts`, `gradle/libs.versions.toml`, `AndroidManifest.xml`, `MainActivity.kt`, and `.gitignore`.

**3. Generate a keystore**
```
/droidforge:keystore MyApp
```
Shows the full `keytool` command, asks for confirmation, then runs it and outputs the signing config block.

**4. Before submitting to Play Store**
```
/droidforge:release-checklist
```
Interactive section-by-section checklist covering build, testing, Play Console, content, and post-submission.

---

## Commands

| Command | Description |
|---|---|
| `/droidforge:setup` | One-time setup — saves your Android developer conventions |
| `/droidforge:new-app` | Scaffold a complete new Android app with all files |
| `/droidforge:keystore` | Generate a keystore (shows keytool command, asks first) |
| `/droidforge:signing-config` | Write signing config for build.gradle.kts |
| `/droidforge:version-bump` | Bump versionCode and versionName (patch / minor / major) |
| `/droidforge:gradle-update` | Update version catalog with compatibility checks |
| `/droidforge:release-checklist` | Interactive pre-submission checklist for Play Store |

---

## Agents

Triggered automatically when relevant, or explicitly invoked:

| Agent | Purpose |
|---|---|
| `setup-agent` | Scaffolds complete Android project files |
| `gradle-agent` | Handles Gradle / version catalog issues and updates |
| `release-agent` | Version bump, changelog generation, git tagging |

---

## Skills

Loaded automatically by Claude when relevant context is detected:

| Skill | Loaded when... |
|---|---|
| `keystore-conventions` | Creating keystores or configuring signing |
| `package-naming` | Creating new apps or setting up package names |
| `gradle-best-practices` | Editing build.gradle.kts or libs.versions.toml |
| `multi-app-structure` | Working across multiple apps or managing a portfolio |
| `release-workflow` | Preparing a release or building a signed AAB |

---

## Hooks

| Hook | When it fires |
|---|---|
| `pre-build-check` | Before `gradlew bundleRelease` / `assembleRelease` — warns if signing config or keystore is missing |
| `post-version-bump` | After `build.gradle.kts` version change — reminds about changelog and git tag |

---

## How It Works

```
/droidforge:setup ──► .claude-plugin-config.json (local only)
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        new-app           keystore        version-bump
        signing-config    gradle-update   release-checklist
```

- **setup** — saves your conventions once, all commands read from it silently
- **setup-agent** — scaffolds complete Android project files on demand
- **gradle-agent** — enforces AGP ↔ Gradle ↔ Kotlin ↔ Compose compatibility
- **release-agent** — version bump, changelog from git log, annotated tags

---

## Plugin Structure

```
DroidForge/
├── .claude-plugin/
│   ├── plugin.json              # Plugin manifest
│   └── marketplace.json         # Marketplace listing
├── commands/                    # setup, new-app, keystore, signing-config,
│                                #   version-bump, gradle-update, release-checklist
├── agents/                      # setup-agent, gradle-agent, release-agent
├── skills/                      # keystore-conventions, package-naming,
│                                #   gradle-best-practices, multi-app-structure,
│                                #   release-workflow
├── hooks/                       # pre-build-check, post-version-bump
├── README.md
├── DOCUMENTATION.md
├── CHANGELOG.md
└── LICENSE
```

---

## Troubleshooting

**"Run /droidforge:setup first"** — Run `/droidforge:setup` in your project directory to create the config file.

**`keytool: command not found`** — Install a JDK or add Android Studio's bundled JDK to your PATH. See [DOCUMENTATION.md](DOCUMENTATION.md#troubleshooting) for platform-specific instructions.

**AGP / Gradle sync failure** — Update `gradle-wrapper.properties` to a compatible Gradle version. See the [Gradle Compatibility Matrix](DOCUMENTATION.md#gradle-compatibility-matrix).

---

## Documentation

For full details — all command examples, Gradle compatibility matrix, troubleshooting, and plugin architecture — see [DOCUMENTATION.md](DOCUMENTATION.md).

---

## Requirements

- Claude Code
- `keytool` in PATH for `/droidforge:keystore` (part of any Java JDK)
- No external MCP servers required

---

## Privacy Policy

[View Privacy Policy](https://sudarshanchaudhari.github.io/droidforge-claude-plugin-privacy-policy/)

---

## Author

**SUDARSHANCHAUDHARI** — [github.com/SUDARSHANCHAUDHARI](https://github.com/SUDARSHANCHAUDHARI)
SudarshanTechLabs | sudarshantechlabs@gmail.com

---

## License

MIT — see [LICENSE](LICENSE)
