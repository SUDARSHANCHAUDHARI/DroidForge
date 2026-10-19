---
description: Generate a new keystore for an Android app using your saved DroidForge conventions.
argument-hint: "[AppName]"
allowed-tools: Read, Write, Bash, AskUserQuestion
---

Generate a new keystore for an Android app following config-based conventions.

## Config loading

First, read `.claude-plugin-config.json` from the current directory.
- If found: load silently and proceed.
- If not found: stop immediately and output: "Run /droidforge:setup first."

## Steps

1. Ask for:
   - App name (used as keystore alias)
   - Derive alias as `[appname_lowercase]` (lowercase, no spaces or special characters)
   - Check the password is available without printing it: `[ -n "$DROIDFORGE_KEYSTORE_PASSWORD" ] && echo set || echo missing`
     - If missing: tell the user to `export DROIDFORGE_KEYSTORE_PASSWORD='...'` in their shell profile and restart Claude Code, or run the command below themselves in a terminal where it is set. Never ask for the password in chat.

2. Build the keytool command and display it clearly to the user. DO NOT run it yet:

```bash
keytool -genkeypair \
  -alias [appname_lowercase] \
  -keypass:env DROIDFORGE_KEYSTORE_PASSWORD \
  -storepass:env DROIDFORGE_KEYSTORE_PASSWORD \
  -keystore [appname_lowercase].jks \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000 \
  -dname "CN={config.android.keystore_cn}, OU=Mobile, O={config.android.keystore_cn}, L={config.developer.city}, ST={config.developer.city}, C={config.android.keystore_country_code}"
```

3. Ask explicitly: "Run this keytool command now? (y/n)"
   - If n: output the command for manual use and stop.
   - If y: run the command using Bash tool.

4. After running, verify the keystore was created successfully:
```bash
keytool -list -v -keystore [appname_lowercase].jks -storepass:env DROIDFORGE_KEYSTORE_PASSWORD
```
   Show the verification output. If the command fails, show the error and stop.

5. Show the local.properties entries for signing, then tell the user to run `/droidforge:signing-config` to generate the `app/build.gradle.kts` block that reads them. Never put a password literal in `build.gradle.kts`.

```properties
# Add to local.properties yourself (never commit this file; never paste the password into chat)
KEYSTORE_PATH=[appname_lowercase].jks
KEYSTORE_PASSWORD=<your keystore password>
KEY_ALIAS=[appname_lowercase]
KEY_PASSWORD=<your keystore password>
```

6. Remind the user:
   ```
   KEYSTORE CREATED: [appname_lowercase].jks
   ──────────────────────────────────────────
   ⚠  Add *.jks to .gitignore — never commit keystores
   ⚠  Back up this file to secure cloud storage immediately
   ⚠  Losing this keystore = cannot update the app on Play Store
   ✓  Keystore password taken from $DROIDFORGE_KEYSTORE_PASSWORD (not stored by DroidForge)
   ✓  Validity: 10000 days (~27 years)
   ```
