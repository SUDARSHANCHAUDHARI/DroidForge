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
   - Confirm: "Use standard keystore password from config? (y/n)"
     - If n: ask for custom password and confirm it

2. Build the keytool command and display it clearly to the user. DO NOT run it yet:

```bash
keytool -genkeypair \
  -alias [appname_lowercase] \
  -keypass {config.android.keystore_password} \
  -storepass {config.android.keystore_password} \
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
keytool -list -v -keystore [appname_lowercase].jks -storepass {config.android.keystore_password}
```
   Show the verification output. If the command fails, show the error and stop.

5. Output the signing config block for `app/build.gradle.kts`:

```kotlin
signingConfigs {
    create("release") {
        storeFile = file("[appname_lowercase].jks")
        storePassword = "{config.android.keystore_password}"
        keyAlias = "[appname_lowercase]"
        keyPassword = "{config.android.keystore_password}"
    }
}
```

   Also show the recommended local.properties approach:

```properties
# Add to local.properties (never commit this file)
KEYSTORE_PATH=[appname_lowercase].jks
KEYSTORE_PASSWORD={config.android.keystore_password}
KEY_ALIAS=[appname_lowercase]
KEY_PASSWORD={config.android.keystore_password}
```

6. Remind the user:
   ```
   KEYSTORE CREATED: [appname_lowercase].jks
   ──────────────────────────────────────────
   ⚠  Add *.jks to .gitignore — never commit keystores
   ⚠  Back up this file to secure cloud storage immediately
   ⚠  Losing this keystore = cannot update the app on Play Store
   ✓  Keystore password matches your DroidForge config
   ✓  Validity: 10000 days (~27 years)
   ```
