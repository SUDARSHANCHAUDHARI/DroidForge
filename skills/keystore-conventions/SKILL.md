---
name: keystore-conventions
description: Android keystore generation standards for DroidForge users — RSA 2048, 10000-day validity, consistent alias and password conventions. Loaded when creating a keystore, signing config, or new Android app.
trigger: when creating a keystore, configuring signing, or scaffolding a new Android app
---

## Android Keystore Standards

### Standard parameters

| Field       | Value                                       |
|-------------|---------------------------------------------|
| Algorithm   | RSA                                         |
| Key size    | 2048 bits                                   |
| Validity    | 10000 days (~27 years)                      |
| Key alias   | [appname_lowercase] (e.g. taskmaster)       |
| Key pass    | from config: `{config.android.keystore_password}` |
| Store pass  | same as key pass (consistent for simplicity)|
| CN          | `{config.android.keystore_cn}`              |
| OU          | Mobile                                      |
| O           | `{config.android.keystore_cn}`              |
| L           | `{config.developer.city}`                   |
| ST          | `{config.developer.city}`                   |
| C           | `{config.android.keystore_country_code}`    |

### Filename convention

`[appname_lowercase].jks`

Example: app "TaskMaster" → `taskmaster.jks`, alias `taskmaster`

### Standard keytool command

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

### Security rules

- Never commit `.jks` files — always in `.gitignore` as `*.jks`
- Never store keystore password in any tracked file
- Keep keystores in a secure, backed-up location outside the git repo
- Back up to encrypted cloud storage immediately after creation

### Critical warning

**Losing a keystore = cannot update the app on Play Store.** The only option is to publish a new app listing and lose all existing installs and reviews. Always back up.

### Play App Signing (recommended)

Google Play App Signing adds a second layer of protection:
- Your `.jks` becomes the **upload key** — used only to upload the AAB
- Google generates and manages the **app signing key** — used to sign APKs delivered to users
- Even if you lose the upload key, Google can generate a new one
- Enroll via: Play Console → [App] → Release → Setup → App signing

### Verification after creation

```bash
keytool -list -v -keystore [appname_lowercase].jks -storepass {config.android.keystore_password}
```
