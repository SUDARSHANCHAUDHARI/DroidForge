# DroidForge

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](.claude-plugin/plugin.json)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
![Platform](https://img.shields.io/badge/platform-Claude%20Code-blueviolet)
![Target](https://img.shields.io/badge/target-Android%20%2F%20Google%20Play-brightgreen)

> Automate every repetitive Android dev task — keystore creation, signing config, version bumping, Gradle version catalog management, new app scaffolding, and release checklists.

**DroidForge** is a Claude Code plugin that encodes the entire Android release-preparation
layer into repeatable commands, agents, skills, and hooks — built from managing 22+ Android
apps in production under SudarshanTechLabs.

## Table of Contents

- [Overview](#overview)
- [What It Does](#what-it-does)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Commands](#commands)
- [Agents](#agents)
- [Skills](#skills)
- [Hooks](#hooks)
- [How It Works](#how-it-works)
- [Plugin Structure](#plugin-structure)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)
- [Requirements](#requirements)
- [Privacy Policy](#privacy-policy)
- [License](#license)
- [About](#about)

## Overview

By app number twenty, the Android release checklist was twelve manual steps. Keystore signing
errors were occurring because the signing config wasn't regenerated after credential changes.
Version codes were being submitted unchanged because `versionCode` lived in `build.gradle.kts`
alongside everything else and was easy to miss.

DroidForge encodes the entire Android release preparation layer — signing config generation,
version management, Gradle catalog updates, pre-submission checklist — into repeatable commands.
Each command was built in response to a specific failure at fleet scale, not as a philosophical
preference for automation.

The plugin manages 22+ Android apps in production under SudarshanTechLabs.

## What It Does

1. Run `/droidforge:setup` once — saves your developer conventions locally per project
2. Scaffold a complete new Android app with correct package names, signing config, and version catalog
3. Generate keystores with consistent conventions — shows the `keytool` command, asks before running
4. Bump `versionCode` and `versionName` with semver (patch / minor / major)
5. Update `libs.versions.toml` with compatibility checks (AGP ↔ Gradle ↔ Kotlin ↔ Compose)
6. Run an interactive pre-submission checklist before every Play Store release

## Installation

**Step 1 — Add the marketplace**
```bash
/plugin marketplace add SUDARSHANCHAUDHARI/DroidForge
```

**Step 2 — Install the plugin**
```bash
/plugin install droidforge
```

Run `/droidforge:setup` once per project to save your conventions. All other commands use your
saved config automatically — no repeated questions, no hardcoded values.

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

## Agents

Triggered automatically when relevant, or explicitly invoked:

| Agent | Purpose |
|---|---|
| `setup-agent` | Scaffolds complete Android project files |
| `gradle-agent` | Handles Gradle / version catalog issues and updates |
| `release-agent` | Version bump, changelog generation, git tagging |

## Skills

Loaded automatically by Claude when relevant context is detected:

| Skill | Loaded when... |
|---|---|
| `keystore-conventions` | Creating keystores or configuring signing |
| `package-naming` | Creating new apps or setting up package names |
| `gradle-best-practices` | Editing build.gradle.kts or libs.versions.toml |
| `multi-app-structure` | Working across multiple apps or managing a portfolio |
| `release-workflow` | Preparing a release or building a signed AAB |

## Hooks

| Hook | When it fires |
|---|---|
| `pre-build-check` | Before `gradlew bundleRelease` / `assembleRelease` — warns if signing config or keystore is missing |
| `post-version-bump` | After `build.gradle.kts` version change — reminds about changelog and git tag |

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

## Troubleshooting

**"Run /droidforge:setup first"** — Run `/droidforge:setup` in your project directory to create the config file.

**`keytool: command not found`** — Install a JDK or add Android Studio's bundled JDK to your PATH. See [DOCUMENTATION.md](DOCUMENTATION.md#troubleshooting) for platform-specific instructions.

**AGP / Gradle sync failure** — Update `gradle-wrapper.properties` to a compatible Gradle version. See the [Gradle Compatibility Matrix](DOCUMENTATION.md#gradle-compatibility-matrix).

## Documentation

For full details — all command examples, Gradle compatibility matrix, troubleshooting, and plugin architecture — see [DOCUMENTATION.md](DOCUMENTATION.md).

## Requirements

- Claude Code
- `keytool` in PATH for `/droidforge:keystore` (part of any Java JDK)
- No external MCP servers required

## Privacy Policy

[View Privacy Policy](https://sudarshanchaudhari.github.io/droidforge-claude-plugin-privacy-policy/)

## License

MIT — see [LICENSE](LICENSE).

---

## About

I'm Sudarshan Chaudhari, a Senior Quality Engineer, Test Automation specialist, and AI systems builder based in Bangkok, Thailand.

I have 13+ years of experience in software quality engineering, working across SaaS, fintech, gaming, web, mobile, cloud, and digital signage platforms. My background combines hands-on test automation with QA leadership, test strategy, CI/CD, release quality, production investigation, and cross-platform validation.

Alongside my professional QA career, I run [SudarshanTechLabs](https://sudarshantechlabs.com/), my independent engineering and product lab where I design, build, test, and ship software across Android, web, AI, cybersecurity, developer tooling, and cross-platform applications.

### What I work on

- ⚙️ **Quality Engineering & Test Automation** — Playwright, Selenium, Cypress, Appium, API testing, automation frameworks, end-to-end testing, CI/CD, release gates, GitHub Actions, risk-based testing, and production validation
- 🤖 **AI Systems & Automation** — AI agents, multi-agent orchestration, MCP servers, AI-assisted QA, prompt tooling, developer workflows, automation systems, and Claude Code plugins
- 📱 **Mobile & Cross-Platform Applications** — Android applications built with Kotlin and Jetpack Compose, Google Play releases, automated build and publishing pipelines, and cross-platform development spanning iOS, web, Windows, and macOS
- 🌐 **Web Applications & Platforms** — Full-stack applications using Next.js, TypeScript, Firebase, Cloudflare, REST APIs, and modern web infrastructure
- 🛠️ **Developer Tooling & CLI Engineering** — Rust, Python, TypeScript, CLI utilities, multi-repository tooling, build automation, release tooling, and engineering productivity systems
- 🛡️ **Cybersecurity & Observability** — Threat detection, log analysis, security auditing, vulnerability assessment, monitoring, and security-focused developer tools
- 📺 **Digital Signage & Device Platforms** — Content validation, playback testing, device compatibility, production investigation, monitoring, and QA across diverse hardware and operating-system environments

My work sits at the intersection of quality engineering, automation, AI, and software development. I approach products with a QA mindset from the beginning: understanding failure modes, designing for testability, automating repetitive work, and building release confidence into the engineering process.

Through SudarshanTechLabs, I also build products and tools from idea to production, covering architecture, development, testing, CI/CD, release automation, monitoring, and ongoing maintenance.

🌐 [sudarshantechlabs.com](https://sudarshantechlabs.com/) · 💼 [LinkedIn](https://linkedin.com/in/sudarshan-chaudhari) · 🐙 [GitHub](https://github.com/SUDARSHANCHAUDHARI) · ✉️ [sunny.sudarshan@gmail.com](mailto:sunny.sudarshan@gmail.com)
