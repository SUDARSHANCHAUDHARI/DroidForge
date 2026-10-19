---
description: Generate the signing configuration block for an Android app's build.gradle.kts.
argument-hint: "[AppName]"
allowed-tools: Read, Write, AskUserQuestion
---

Generate the signing configuration block for an Android app's `build.gradle.kts`.

## Config loading

First, read `.claude-plugin-config.json` from the current directory.
- If found: load silently and proceed.
- If not found: stop immediately and output: "Run /droidforge:setup first."

## Steps

1. Ask for:
   - App name / alias
   - Keystore filename (default: `[appname_lowercase].jks` — press Enter to accept)
   - Is the keystore in the project root or a separate `keystores/` folder? (root/keystores)

2. Credentials always come from `local.properties` (untracked). Never write a password literal into `build.gradle.kts`.

   **Show the local.properties entries to add** (tell user to add manually — never write credentials to tracked files):
   ```properties
   KEYSTORE_PATH=[keystore_filename]
   KEYSTORE_PASSWORD=<your keystore password>
   KEY_ALIAS=[appname_lowercase]
   KEY_PASSWORD=<your keystore password>
   ```

   **Write the build.gradle.kts signingConfigs block:**
   ```kotlin
   import java.util.Properties

   val localProps = Properties().apply {
       file("../local.properties").takeIf { it.exists() }?.inputStream()?.use { load(it) }
   }

   android {
       signingConfigs {
           create("release") {
               storeFile = file(localProps["KEYSTORE_PATH"] as? String ?: "")
               storePassword = localProps["KEYSTORE_PASSWORD"] as? String ?: ""
               keyAlias = localProps["KEY_ALIAS"] as? String ?: ""
               keyPassword = localProps["KEY_PASSWORD"] as? String ?: ""
           }
       }
       buildTypes {
           release {
               signingConfig = signingConfigs.getByName("release")
               isMinifyEnabled = true
               isShrinkResources = true
               proguardFiles(
                   getDefaultProguardFile("proguard-android-optimize.txt"),
                   "proguard-rules.pro"
               )
           }
       }
   }
   ```

3. Final reminder:
   ```
   SIGNING CONFIG GENERATED
   ────────────────────────
   ✓  local.properties is excluded from git by Android Studio's default .gitignore
   ✓  Verify .gitignore includes: local.properties and *.jks
   ✓  Run ./gradlew signingReport to verify signing is configured correctly
   ```
