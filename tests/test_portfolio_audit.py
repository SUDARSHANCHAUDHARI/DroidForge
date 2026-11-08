import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import portfolio_audit as pa  # noqa: E402

# The "password written in the build file" check has no unit test: a fixture with a literal keystore
# password is blocked by the repository's security scan before it can be written.

GOOD_KTS = """
android {
    compileSdk = 36
    defaultConfig {
        minSdk = 24
        targetSdk = 36
        versionCode = 12
        versionName = "1.4.0"
    }
    buildTypes {
        getByName("release") {
            isMinifyEnabled = true
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
"""

OLD_GROOVY = """
android {
    compileSdkVersion 33
    defaultConfig {
        minSdkVersion 21
        targetSdkVersion 33
        versionCode 3
        versionName "0.9"
    }
    buildTypes { release { minifyEnabled false } }
}
"""

CATALOG_KTS = """
android {
    compileSdk = libs.versions.compileSdk.get().toInt()
    defaultConfig { targetSdk = libs.versions.targetSdk.get().toInt(); versionCode = 7; versionName = "2.0.0" }
    buildTypes { release { isMinifyEnabled = true; signingConfig = signingConfigs.getByName("release") } }
}
"""
TOML = '[versions]\nagp = "8.9.1"\nkotlin = "2.1.20"\ncompileSdk = "36"\ntargetSdk = "35"\n\n[libraries]\nx = "y"\n'


def make(root, name, build, groovy=False, toml=None):
    repo = Path(root) / name
    (repo / "app").mkdir(parents=True)
    (repo / "app" / ("build.gradle" if groovy else "build.gradle.kts")).write_text(build)
    if toml:
        (repo / "gradle").mkdir()
        (repo / "gradle" / "libs.versions.toml").write_text(toml)
    return repo


def clean_git(_repo):
    return "main", 0


class Audit(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_good_app_has_no_issues(self):
        repo = make(self.root, "TrailMap", GOOD_KTS)
        r = pa.audit_app(repo, 35, tracked=lambda _r: ["app/build.gradle.kts"], git=clean_git)
        self.assertEqual((r["versionCode"], r["versionName"]), ("12", "1.4.0"))
        self.assertEqual((r["minSdk"], r["targetSdk"], r["compileSdk"]), ("24", "36", "36"))
        self.assertTrue(r["releaseSigning"] and r["minify"])
        self.assertEqual(r["issues"], [])

    def test_old_groovy_app_flags_its_problems(self):
        repo = make(self.root, "OldApp", OLD_GROOVY, groovy=True)
        tracked = lambda _r: ["app/build.gradle", "app/release.jks", "keystore.properties"]
        r = pa.audit_app(repo, 35, tracked=tracked, git=lambda _r: ("dev", 2))
        self.assertEqual((r["versionCode"], r["versionName"], r["targetSdk"]), ("3", "0.9", "33"))
        self.assertEqual((r["branch"], r["uncommitted"]), ("dev", 2))
        text = " | ".join(r["issues"])
        for expected in ("app/release.jks, keystore.properties", "no signingConfig",
                         "does not enable minify", "targetSdk 33 is below 35"):
            self.assertIn(expected, text)

    def test_version_catalog_references_resolved(self):
        repo = make(self.root, "Cat", CATALOG_KTS, toml=TOML)
        r = pa.audit_app(repo, None, tracked=lambda _r: [], git=clean_git)
        self.assertEqual((r["targetSdk"], r["compileSdk"], r["agp"], r["kotlin"]), ("35", "36", "8.9.1", "2.1.20"))
        self.assertEqual(r["issues"], [])

    def test_no_floor_means_no_target_issue_and_not_git_is_reported(self):
        repo = make(self.root, "OldApp", OLD_GROOVY, groovy=True)
        r = pa.audit_app(repo, None, tracked=lambda _r: None, git=lambda _r: (None, None))
        self.assertFalse(any("below" in i for i in r["issues"]))
        self.assertIn("not a git repository", r["issues"])

    def test_version_properties_convention(self):
        build = GOOD_KTS.replace("versionCode = 12", "versionCode = appVersionCode") \
                        .replace('versionName = "1.4.0"', "versionName = appVersionName")
        build = 'val versionPropertiesFile = rootProject.file("config/version.properties")\n' + build
        repo = make(self.root, "PropsApp", build)
        (repo / "config").mkdir()
        (repo / "config" / "version.properties").write_text(
            "# comment\nVERSION_MAJOR=2\nVERSION_MINOR=3\nVERSION_PATCH=1\nVERSION_CODE=41\n")
        r = pa.audit_app(repo, None, tracked=lambda _r: [], git=clean_git)
        self.assertEqual((r["versionCode"], r["versionName"]), ("41", "2.3.1"))
        self.assertNotIn("versionCode not found", r["issues"])

    def test_signing_config_through_a_variable_counts(self):
        build = GOOD_KTS.replace('signingConfig = signingConfigs.getByName("release")',
                                 'val releaseConfig = signingConfigs.getByName("release")\n'
                                 '            signingConfig = releaseConfig')
        r = pa.audit_app(make(self.root, "VarApp", build), None, tracked=lambda _r: [], git=clean_git)
        self.assertTrue(r["releaseSigning"])

    def test_find_apps_depth_and_skips(self):
        make(self.root, "A", GOOD_KTS)
        make(self.root / "group", "B", GOOD_KTS)
        make(self.root / "node_modules", "C", GOOD_KTS)
        make(self.root / "a" / "b" / "c", "TooDeep", GOOD_KTS)
        self.assertEqual(sorted(p.name for p in pa.find_apps(self.root)), ["A", "B"])

    def test_main_json_and_empty(self):
        make(self.root, "A", GOOD_KTS)
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(pa.main([str(self.root), "--json"]), 0)
        self.assertEqual(json.loads(buf.getvalue())[0]["app"], "A")
        with tempfile.TemporaryDirectory() as empty, redirect_stdout(io.StringIO()) as out:
            self.assertEqual(pa.main([empty]), 0)
        self.assertIn("no Android apps", out.getvalue())
        self.assertEqual(pa.main([str(self.root / "missing")]), 2)


if __name__ == "__main__":
    unittest.main()
