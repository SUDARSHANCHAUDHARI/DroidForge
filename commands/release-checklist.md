---
description: Run a pre-release checklist before submitting an Android app to Google Play.
argument-hint: "[AppName]"
allowed-tools: Read, Bash, AskUserQuestion
---

Run a pre-release checklist before submitting an Android app to Google Play.

## Config loading

First, read `.claude-plugin-config.json` from the current directory.
- If found: load silently and proceed.
- If not found: stop immediately and output: "Run /droidforge:setup first."

## Steps

Go through each section interactively. Present each item, wait for the user to confirm done/pending/na before moving to the next section.

Read `app/build.gradle.kts` first to extract the current `versionCode` and `versionName` to display in the checklist.

---

### Section 1 — Build

Present these items and ask user to mark each as done (✓), pending (…), or n/a (–):

- [ ] `versionCode` incremented from last Play Store release (current: [versionCode from build file])
- [ ] `versionName` updated (current: "[versionName from build file]")
- [ ] Release AAB built with release signing config (not debug): `./gradlew bundleRelease`
- [ ] ProGuard/R8 enabled for release build (`isMinifyEnabled = true`)
- [ ] Build passes without errors or warnings

Ask: "Section 1 complete? Press Enter to continue to Testing."

---

### Section 2 — Testing

- [ ] Tested on at least one physical device
- [ ] Tested on Android 7+ (minSdk compliance)
- [ ] Crash-free on all core user flows
- [ ] No debug logs, debug toasts, or test features visible in release build
- [ ] Back button and navigation behave correctly

Ask: "Section 2 complete? Press Enter to continue to Play Console."

---

### Section 3 — Play Console

- [ ] Store listing is up to date
- [ ] Screenshots are current (no old UI, no test data visible)
- [ ] Release notes written for this version
- [ ] Data safety section accurate and reflects current app behaviour
- [ ] Content rating current and accurate
- [ ] All policy declarations up to date (financial features, AI-generated content, etc.)

Ask: "Section 3 complete? Press Enter to continue to App Content."

---

### Section 4 — App Content

- [ ] Privacy policy URL live and accessible
  (Expected: `{config.github_pages.privacy_policy_pattern}` — substitute `{appname}` for this app)
- [ ] Privacy policy content matches actual data the app collects
- [ ] App permissions in manifest match features used — no unused permissions declared
- [ ] Sensitive permissions (CAMERA, LOCATION, CONTACTS, etc.) have clear user-facing justification

Ask: "Section 4 complete? Press Enter to continue to Post-Submission."

---

### Section 5 — Post-Submission

- [ ] Git tag created for this release version: `git tag -a v[versionName] -m "Release [versionName]"`
- [ ] Tag pushed to remote: `git push origin v[versionName]`
- [ ] Release notes committed to repo (CHANGELOG.md or similar)
- [ ] App tracker spreadsheet / notes updated with release date and version

---

### Summary

After all sections, output:

```
RELEASE CHECKLIST COMPLETE
───────────────────────────
App:         [AppName if provided, else current directory]
Version:     [versionName] (code: [versionCode])
Date:        [today's date]

✓ Done:    [count]
…  Pending: [count]
–  N/A:     [count]

[If any pending items:]
⚠  Resolve pending items before submitting to Play Store.

[If all done or n/a:]
✓  All items resolved. Ready to submit.
```
