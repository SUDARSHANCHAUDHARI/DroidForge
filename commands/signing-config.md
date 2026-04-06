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
   - Use `local.properties` for credentials? (y/n — recommended yes)

2. If using `local.properties` (recommended):

   **Show the local.properties entries to add** (tell user to add manually — never write credentials to tracked files):
   ```properties
   KEYSTORE_PATH=[keystore_filename]
   KEYSTORE_PASSWORD={config.android.keystore_password}
   KEY_ALIAS=[appname_lowercase]
   KEY_PASSWORD={config.android.keystore_password}
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

3. If NOT using `local.properties` (not recommended — warn user):

   **Output warning:**
   ```
   ⚠  WARNING: Hardcoding credentials in build.gradle.kts is not recommended.
   These values will be visible in your git history if committed.
   Consider using local.properties instead.
   ```

   **Then output the direct approach:**
   ```kotlin
   android {
       signingConfigs {
           create("release") {
               storeFile = file("[keystore_filename]")
               storePassword = "{config.android.keystore_password}"
               keyAlias = "[appname_lowercase]"
               keyPassword = "{config.android.keystore_password}"
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

4. Final reminder:
   ```
   SIGNING CONFIG GENERATED
   ────────────────────────
   ✓  local.properties is excluded from git by Android Studio's default .gitignore
   ✓  Verify .gitignore includes: local.properties and *.jks
   ✓  Run ./gradlew signingReport to verify signing is configured correctly
   ```
