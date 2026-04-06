---
name: release-workflow
description: End-to-end Android app release workflow for solo developers — pre-release steps, build commands, ADB install testing, Play Console submission, post-release git tagging, and staged rollout strategy.
trigger: when preparing a release, building a signed AAB, or submitting to Play Store
---

## Solo Developer Android Release Workflow

### Step 1 — Pre-release

1. Bump `versionCode` (+1 always) and `versionName` (semver) using `/droidforge:version-bump`
2. Write release notes for this version (what changed for users, not internal details)
3. Verify `isMinifyEnabled = true` and `isShrinkResources = true` in release buildType
4. Run clean build:
   ```bash
   ./gradlew clean bundleRelease
   ```
5. Verify the AAB is signed with the release key (not debug):
   ```bash
   ./gradlew signingReport
   ```

### Step 2 — Test before submitting

```bash
# Build a release APK for local testing
./gradlew assembleRelease

# Install on connected device
adb install -r app/build/outputs/apk/release/app-release.apk
```

Testing checklist:
- Run through all core user flows
- Confirm no debug toasts, logs, or test features visible
- Test on a device running the minimum supported Android version
- Verify in-app purchases / ads work in release mode (sandbox for IAP)

### Step 3 — Play Console submission

1. Open Play Console → [App] → Release → Production
2. Create new release
3. Upload the AAB from `app/build/outputs/bundle/release/app-release.aab`
4. Paste release notes (use the same text you prepared in Step 1)
5. Resolve any policy warnings (yellow/red banners)
6. Review and submit

### Step 4 — Post-release

```bash
# Create annotated tag (show to user, confirm before running)
git tag -a v[versionName] -m "Release [versionName] — [brief description]"

# Push tag
git push origin v[versionName]
```

Update app tracker with: release date, new version, Play review status.

Monitor Play Console for 24–48 hours after rollout:
- Crash-free rate (target: > 99%)
- ANR rate (target: < 0.47% — Google's policy threshold)
- User reviews mentioning crashes

### Staged rollout strategy

Never release to 100% immediately for production apps:

| Stage | Rollout % | Wait |
|-------|-----------|------|
| 1     | 10–20%    | 24h  |
| 2     | 50%       | 24h  |
| 3     | 100%      | —    |

**Halt rollout** and investigate if:
- Crash-free rate drops below 99%
- ANR rate exceeds 0.47%
- Sudden spike in 1-star reviews

To halt: Play Console → [App] → Release → Production → Halt rollout

### Build output locations

| Output | Path |
|--------|------|
| Release AAB | `app/build/outputs/bundle/release/app-release.aab` |
| Release APK | `app/build/outputs/apk/release/app-release.apk` |
| Mapping file | `app/build/outputs/mapping/release/mapping.txt` |

Upload `mapping.txt` to Play Console for deobfuscated crash reports.

### Play Store submission checklist

Run `/droidforge:release-checklist` before every submission. Key items:
- `versionCode` > last published version
- Release signing config confirmed (not debug)
- Privacy policy URL live and correct
- Store listing current (screenshots show current UI)
- Data safety section accurate
