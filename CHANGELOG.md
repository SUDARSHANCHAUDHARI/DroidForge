# Changelog

All notable changes to DroidForge will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- `/droidforge:portfolio-audit` — read-only audit of every Android app under a folder: versionName
  and versionCode (including the `config/version.properties` convention), min/target/compile SDK
  (including version-catalog references), AGP and Kotlin, release signing, R8, signing files tracked
  by git, a password written in the build file, branch and uncommitted changes. `--min-target N`
  flags apps below a target SDK floor; none is assumed
- `/droidforge:ship` — pre-flight audit, version bump, release checklist and `bundleRelease` in one
  flow with a stop for the user's go at each step; never commits, tags, pushes or uploads
- `scripts/portfolio_audit.py` and `tests/` — stdlib Python, 9 unit tests

## [1.0.0] — 2026-04-06

### Added
- `/droidforge:setup` — one-time per-project setup, saves conventions to `.claude-plugin-config.json`
- `/droidforge:new-app` — scaffold a complete Android app (build.gradle.kts, libs.versions.toml, AndroidManifest.xml, MainActivity.kt, .gitignore)
- `/droidforge:keystore` — generate a keystore with consistent conventions; shows keytool command and waits for explicit confirmation before running
- `/droidforge:signing-config` — generate signing config block for build.gradle.kts using local.properties
- `/droidforge:version-bump` — bump versionCode (+1 always) and versionName (patch / minor / major semver)
- `/droidforge:gradle-update` — update libs.versions.toml with AGP ↔ Gradle ↔ Kotlin ↔ Compose compatibility checks
- `/droidforge:release-checklist` — interactive section-by-section pre-submission checklist for Google Play
- `setup-agent` — autonomous Android project scaffolding agent
- `gradle-agent` — Gradle/version catalog expert agent with compatibility rules
- `release-agent` — version bump, changelog generation, and git tagging agent
- `keystore-conventions` skill — RSA 2048, 10000-day validity, consistent alias/password conventions
- `package-naming` skill — package name format rules, privacy policy URL pattern, repo naming
- `gradle-best-practices` skill — Kotlin DSL, version catalog, Kotlin 2.0+ Compose setup, ProGuard
- `multi-app-structure` skill — managing a large Android app portfolio as a solo developer
- `release-workflow` skill — end-to-end release workflow from pre-release to staged rollout
- `pre-build-check` hook — warns before release builds if signing config or keystore is missing
- `post-version-bump` hook — reminds about changelog and git tag after version change
- MIT License
