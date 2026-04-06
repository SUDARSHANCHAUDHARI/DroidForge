---
name: gradle-best-practices
description: Gradle Kotlin DSL and version catalog best practices for Android projects in 2025-2026 — covers TOML version catalog, Kotlin 2.0+ Compose setup, SDK targets, ProGuard, and AGP compatibility. Loaded when editing Gradle files.
trigger: when editing build.gradle.kts, libs.versions.toml, or any Gradle settings files
---

## Gradle Best Practices for Android (2025–2026)

### Always use version catalog

- All dependency versions belong in `gradle/libs.versions.toml` — never hardcode versions in `build.gradle.kts`
- Reference with type-safe accessors: `implementation(libs.androidx.core.ktx)` not `implementation("androidx.core:core-ktx:1.13.1")`
- BOM imports: `implementation(platform(libs.androidx.compose.bom))`

### Kotlin DSL (.kts) rules

- Use `implementation(libs.xxx)` — never Groovy syntax like `implementation 'xxx:yyy:1.0'`
- Type-safe accessors are preferred over string-based references
- `buildFeatures { compose = true }` required for Compose projects

### Kotlin 2.0+ Compose setup (current standard)

```kotlin
// In plugins block of app/build.gradle.kts:
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)   // ← required for Kotlin 2.0+
}
```

```toml
# In libs.versions.toml plugins block:
[plugins]
kotlin-compose = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
```

**Do NOT use** `kotlinOptions { kotlinCompilerExtensionVersion = "..." }` — this is deprecated for Kotlin 2.0+.

### SDK target versions (2025)

```kotlin
android {
    compileSdk = 35      // Android 15 — current as of 2025
    defaultConfig {
        minSdk = 24      // Android 7.0 — ~96% device coverage
        targetSdk = 35
    }
}
```

**Play Store requirement**: `targetSdk` must meet Google's current minimum (35 for new submissions as of late 2024). Apps with outdated `targetSdk` receive policy warnings.

### Java / Kotlin compile options

```kotlin
compileOptions {
    sourceCompatibility = JavaVersion.VERSION_11
    targetCompatibility = JavaVersion.VERSION_11
}
kotlinOptions {
    jvmTarget = "11"
}
```

### ProGuard for release builds (required)

```kotlin
buildTypes {
    release {
        isMinifyEnabled = true
        isShrinkResources = true
        proguardFiles(
            getDefaultProguardFile("proguard-android-optimize.txt"),
            "proguard-rules.pro"
        )
    }
}
```

Both `isMinifyEnabled` and `isShrinkResources` must be `true` for release. This reduces APK/AAB size significantly.

### AGP ↔ Gradle wrapper compatibility

| AGP version | Min Gradle version |
|-------------|--------------------|
| 8.5.x       | 8.7+               |
| 8.4.x       | 8.6+               |
| 8.3.x       | 8.4+               |
| 8.2.x       | 8.2+               |

Check `gradle/wrapper/gradle-wrapper.properties` when updating AGP.

### Signing config via local.properties (recommended)

```kotlin
import java.util.Properties

val localProps = Properties().apply {
    file("../local.properties").takeIf { it.exists() }?.inputStream()?.use { load(it) }
}

android {
    signingConfigs {
        create("release") {
            storeFile = file(localProps["KEYSTORE_PATH"] as String)
            storePassword = localProps["KEYSTORE_PASSWORD"] as String
            keyAlias = localProps["KEY_ALIAS"] as String
            keyPassword = localProps["KEY_PASSWORD"] as String
        }
    }
}
```

`local.properties` is excluded from git by Android Studio's default `.gitignore` — never commit it.

### Build commands reference

```bash
./gradlew clean                 # Clean all build outputs
./gradlew bundleRelease         # Build release AAB (for Play Store)
./gradlew assembleRelease       # Build release APK (for direct install)
./gradlew signingReport         # Verify signing configuration
./gradlew dependencies          # Show full dependency tree
```
