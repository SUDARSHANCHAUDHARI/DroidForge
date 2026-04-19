---
description: Scaffold a complete new Android app following your saved DroidForge conventions.
argument-hint: "[AppName]"
allowed-tools: Read, Write, Bash, AskUserQuestion
---

Scaffold a complete new Android app following config-based conventions.

## Config loading

First, read `.claude-plugin-config.json` from the current directory.
- If found: load silently and proceed. All `{config.*}` references below use values from this file.
- If not found: stop immediately and output: "Run /droidforge:setup first."

## Steps

1. Ask for the following (one by one, wait for each answer):
   - App name (e.g. "TaskMaster")
   - App category / purpose (1–2 sentences describing what it does)
   - Minimum SDK version (default: 24 — press Enter to accept)
   - Target SDK version (default: 36 — press Enter to accept)
   - Will it have ads? (AdMob y/n)
   - Will it have in-app purchases? (y/n)

2. Derive the package name:
   - Format: `{config.android.package_prefix}.[appname_lowercase_nospaces]`
   - Strip spaces, hyphens, special characters from the app name, lowercase it
   - Example: "Task Master" → `{config.android.package_prefix}.taskmaster`
   - Show the derived package name and ask user to confirm or override

3. Build the keytool command (show to user, do NOT run it yet):

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

   Ask: "Run keystore generation now? (y/n)"
   - If y: run the command using Bash tool, then verify with:
     `keytool -list -v -keystore [appname_lowercase].jks -storepass {config.android.keystore_password}`
   - If n: remind user to run it manually before building a release

4. Generate the following files (write them to disk):

**app/build.gradle.kts**
```kotlin
import java.util.Properties

val localProps = Properties().apply {
    file("../local.properties").takeIf { it.exists() }?.inputStream()?.use { load(it) }
}

plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
}

android {
    namespace = "[derived_package_name]"
    compileSdk = 36

    defaultConfig {
        applicationId = "[derived_package_name]"
        minSdk = [minSdk]
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    signingConfigs {
        create("release") {
            storeFile = file(localProps["KEYSTORE_PATH"] as? String ?: "[appname_lowercase].jks")
            storePassword = localProps["KEYSTORE_PASSWORD"] as? String ?: ""
            keyAlias = localProps["KEY_ALIAS"] as? String ?: "[appname_lowercase]"
            keyPassword = localProps["KEY_PASSWORD"] as? String ?: ""
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            signingConfig = signingConfigs.getByName("release")
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }

    kotlinOptions {
        jvmTarget = "11"
    }

    buildFeatures {
        compose = true
    }
}

dependencies {
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.graphics)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.ui.test.junit4)
    debugImplementation(libs.androidx.ui.tooling)
    debugImplementation(libs.androidx.ui.test.manifest)
}
```

**gradle/libs.versions.toml** — use current stable versions as of 2025:
```toml
[versions]
agp = "8.9.0"
kotlin = "2.1.20"
coreKtx = "1.15.0"
junit = "4.13.2"
junitVersion = "1.2.1"
espressoCore = "3.6.1"
lifecycleRuntimeKtx = "2.8.7"
activityCompose = "1.10.0"
composeBom = "2025.05.00"

[libraries]
androidx-core-ktx = { group = "androidx.core", name = "core-ktx", version.ref = "coreKtx" }
androidx-lifecycle-runtime-ktx = { group = "androidx.lifecycle", name = "lifecycle-runtime-ktx", version.ref = "lifecycleRuntimeKtx" }
androidx-activity-compose = { group = "androidx.activity", name = "activity-compose", version.ref = "activityCompose" }
androidx-compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "composeBom" }
androidx-ui = { group = "androidx.compose.ui", name = "ui" }
androidx-ui-graphics = { group = "androidx.compose.ui", name = "ui-graphics" }
androidx-ui-tooling-preview = { group = "androidx.compose.ui", name = "ui-tooling-preview" }
androidx-material3 = { group = "androidx.compose.material3", name = "material3" }
junit = { group = "junit", name = "junit", version.ref = "junit" }
androidx-junit = { group = "androidx.test.ext", name = "junit", version.ref = "junitVersion" }
androidx-espresso-core = { group = "androidx.test.espresso", name = "espresso-core", version.ref = "espressoCore" }
androidx-ui-tooling = { group = "androidx.compose.ui", name = "ui-tooling" }
androidx-ui-test-manifest = { group = "androidx.compose.ui", name = "ui-test-manifest" }
androidx-ui-test-junit4 = { group = "androidx.compose.ui", name = "ui-test-junit4" }

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
kotlin-compose = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
```

**local.properties additions** (show separately — DO NOT write to disk; instruct user to add manually):
```properties
KEYSTORE_PATH=[appname_lowercase].jks
KEYSTORE_PASSWORD={config.android.keystore_password}
KEY_ALIAS=[appname_lowercase]
KEY_PASSWORD={config.android.keystore_password}
```

**AndroidManifest.xml** — base manifest with package name

**app/src/main/java/[package/path]/MainActivity.kt** — basic Compose entry point

**proguard-rules.pro** — empty file with comment

**.gitignore** — include `*.jks`, `local.properties`, `.gradle/`, `build/`, `.claude-plugin-config.json`

5. Output a setup summary:

```
NEW APP SCAFFOLDED
──────────────────
App name:       [AppName]
Package:        [derived_package_name]
Min SDK:        [minSdk]
Target SDK:     [targetSdk]
Keystore:       [appname_lowercase].jks (alias: [appname_lowercase])
Privacy policy: {config.github_pages.privacy_policy_pattern}

Files created:
  app/build.gradle.kts
  gradle/libs.versions.toml
  app/src/main/AndroidManifest.xml
  app/src/main/java/.../MainActivity.kt
  proguard-rules.pro
  .gitignore

NEXT STEPS:
1. Add local.properties entries shown above (never commit this file)
2. Run: ./gradlew sync
3. Verify the app builds before adding features
```
