---
name: package-naming
description: Android package naming conventions for DroidForge users — format rules, portfolio consistency, privacy policy URL patterns, and GitHub repo naming. Loaded when creating a new app or setting up package names.
trigger: when creating a new app, setting up a package name, or organizing an app portfolio
---

## Android Package Naming Convention

### Standard format

`{config.android.package_prefix}.[appname]`

Where `{config.android.package_prefix}` is set during `/droidforge:setup` (e.g. `com.yourcompany`).

### Rules for `[appname]`

- Lowercase only
- No spaces, hyphens, or special characters
- No underscores — prefer concatenation (e.g. `taskmanager` not `task_manager`)
- Must be globally unique across the Play Store
- Should reflect the app's core purpose, not just a generic word

### Derivation from app name

| App Name       | Derived appname   | Full package name                               |
|----------------|-------------------|-------------------------------------------------|
| TaskMaster     | taskmaster        | `{config.android.package_prefix}.taskmaster`    |
| Weather Now    | weathernow        | `{config.android.package_prefix}.weathernow`    |
| QR Scanner Pro | qrscannerpro      | `{config.android.package_prefix}.qrscannerpro`  |
| My Budget 2    | mybudget2         | `{config.android.package_prefix}.mybudget2`     |

### Privacy policy URL pattern

`{config.github_pages.privacy_policy_pattern}` — substitute `{appname}` with the app name in lowercase with hyphens.

Example for app "TaskMaster":
`https://[github_username].github.io/taskmaster-privacy-policy/`

The privacy policy page must be live before submitting to Play Store.

### GitHub repository naming

Two acceptable conventions:
- PascalCase: `TaskMaster` (matches the app name exactly)
- kebab-case: `taskmaster-android` (descriptive with platform suffix)

Use PascalCase for consistency when the app name is a single word or compound noun.

### Play Store uniqueness check

Before finalising a package name:
1. Search the Play Store for the app name
2. Check if the exact package ID is already taken (cannot be reused once published)
3. Once published, the package name is **permanent** — it can never be changed for an existing app

### Namespace vs applicationId

In modern Android projects these should always match:
```kotlin
android {
    namespace = "com.yourcompany.taskmaster"   // used for R class resolution
    defaultConfig {
        applicationId = "com.yourcompany.taskmaster"  // used by Play Store
    }
}
```
