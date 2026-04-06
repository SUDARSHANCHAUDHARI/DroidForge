---
event: PostToolUse
matcher: "Write"
description: After a Write tool call that modifies build.gradle.kts, check whether versionCode or versionName changed. If so, remind the user about git tagging and changelog updates.
---

## Post-Version-Bump Hook

This hook fires after Write tool calls that modify `build.gradle.kts`.

### Trigger condition

Only activate when ALL of these are true:
- The Write tool call's file path ends with `build.gradle.kts`
- The written content contains `versionCode` or `versionName`

If neither condition matches, do nothing.

### Action

After a version change is detected in `build.gradle.kts`, remind the user:

```
DroidForge: Version updated in build.gradle.kts

Suggested next steps:
  1. Update CHANGELOG.md with changes in this version
  2. Create a git tag:  git tag -a v[versionName] -m "Release [versionName]"
  3. Run the release checklist:  /droidforge:release-checklist
```

Substitute `[versionName]` with the actual new value found in the written content.

### Behaviour

- Show the reminder once after the version change write
- Do not repeat the reminder if subsequent write calls touch unrelated files
- Keep the message concise — this is a nudge, not a blocker
