---
name: multi-app-structure
description: Managing a portfolio of 20+ Android apps as a solo developer — repo strategy, shared code, keystore management, app tracker, and priority triage when policy changes arrive. Loaded when working across multiple apps.
trigger: when working across multiple apps, setting up a new app, or organizing an app portfolio
---

## Managing a Large Android App Portfolio as a Solo Developer

### Repository strategy

**Option A: One repo per app** (recommended for public apps)
- Each app is its own GitHub repository
- Cleaner per-app CI/CD
- Easier to open-source individual apps
- Naming: `[GitHubUsername]/[AppName]` (PascalCase)

**Option B: Monorepo** (better for code sharing)
- All apps in one repo under `/apps/[appname]/`
- Shared utilities in `/shared/` module as a local library
- Better for enforcing consistent dependencies across all apps
- Harder to open-source individual apps

### Shared code strategy

For common utilities across apps (AdMob helper, in-app review wrapper, crash reporting, network client):

**Option 1: Private GitHub Package (local Maven)**
- Publish shared module as `.aar` to GitHub Packages
- Add as a dependency in each app

**Option 2: Copy-paste for small utilities (acceptable for solo dev)**
- Acceptable when the utility is < 200 lines and rarely changes
- Document which apps share the same version of the utility

**Option 3: Local composite build**
- Keep shared module in a sibling directory
- Use `includeBuild("../shared-module")` in `settings.gradle.kts`
- Best for active development — changes reflect immediately across apps

### Keystore management

- One `.jks` per app (alias = app name lowercase)
- All keystores stored in the same secure, backed-up location outside any git repo
- Use consistent password (from `{config.android.keystore_password}`) for easier management
- All new apps enrolled in Play App Signing — Google holds the app signing key

### App tracker (recommended spreadsheet columns)

| App Name | Package | versionCode | versionName | Last Release | Play Status | targetSdk | Notes |
|----------|---------|-------------|-------------|-------------|-------------|-----------|-------|

Flag apps that:
- Have `targetSdk` below Google's current minimum requirement
- Have outstanding policy warnings in Play Console
- Haven't been updated in 12+ months (may receive policy emails)

### Priority triage when a policy change or Android update arrives

When Google announces a new requirement (e.g. targetSdk deadline, new permission rules):

1. Check Play Console for any policy warning banners across all apps
2. Identify apps with the approaching deadline — check app tracker
3. Update high-revenue / high-install apps first
4. Batch-update utility / minor apps in a single session
5. Use `/droidforge:gradle-update` to update SDK targets across apps

### Release scheduling for 20+ apps

- Never release multiple apps on the same day — stagger by 24–48h to allow crash monitoring
- Keep a release queue: one app in review → next app being prepared
- Use staged rollout for all releases (start at 10–20%)
- Monitor ANR & crash rate in Play Console for 24–48h after each rollout increase

### Privacy policy maintenance

Every app needs a live privacy policy. Pattern: `{config.github_pages.privacy_policy_pattern}`

For portfolio maintenance:
- Host all policies on GitHub Pages under one repository
- Each app gets its own policy page: `[appname]-privacy-policy/index.html`
- Update policy pages when adding new permissions or SDK data collection changes
