#!/usr/bin/env python3
"""Read-only audit of every Android app under a folder: versions, SDK levels, release signing,
minify, keystore files committed to git, and git state. Changes nothing.

usage: portfolio_audit.py <root> [--min-target N] [--json]
  --min-target  flag apps whose targetSdk is below N (Google's current minimum; check Play Console)
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "build", ".gradle", ".idea", "graphify-out"}
MAX_DEPTH = 3
KEY_PATTERNS = ("*.jks", "*.keystore", "keystore.properties", "key.properties")


def find_apps(root):
    """Repo folders (up to MAX_DEPTH below root) that contain app/build.gradle(.kts)."""
    root, found = Path(root), []

    def walk(folder, depth):
        for name in ("build.gradle.kts", "build.gradle"):
            if (folder / "app" / name).is_file():
                found.append(folder)
                return
        if depth >= MAX_DEPTH:
            return
        try:
            children = sorted(p for p in folder.iterdir() if p.is_dir() and p.name not in SKIP_DIRS)
        except OSError:
            return
        for child in children:
            walk(child, depth + 1)

    walk(root, 0)
    return found


def read(path):
    try:
        return Path(path).read_text(errors="replace")
    except OSError:
        return ""


def catalog_versions(repo):
    """[versions] table of gradle/libs.versions.toml as a dict."""
    text, out, in_versions = read(Path(repo) / "gradle" / "libs.versions.toml"), {}, False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("["):
            in_versions = s == "[versions]"
        elif in_versions:
            m = re.match(r'([A-Za-z0-9_.-]+)\s*=\s*"([^"]+)"', s)
            if m:
                out[m.group(1)] = m.group(2)
    return out


def value(build, catalog, *names):
    """A numeric or string setting, either literal or a libs.versions reference."""
    for name in names:
        m = re.search(rf'\b{name}\s*[=(]?\s*"?([0-9][\w.\-]*)"?', build)
        if m:
            return m.group(1)
        m = re.search(rf"\b{name}\s*=?\s*libs\.versions\.([\w.]+)\.get\(\)", build)
        if m:
            key = m.group(1)
            for k in (key, key.replace(".", "-"), key.replace(".", "_")):
                if k in catalog:
                    return catalog[k]
    return None


def build_properties(repo, build):
    """Merged key=value pairs of every .properties file the build file loads via rootProject.file()."""
    props = {}
    for rel in re.findall(r'rootProject\.file\("([^"]+\.properties)"\)', build):
        for line in read(Path(repo) / rel).splitlines():
            m = re.match(r"\s*([\w.\-]+)\s*[=:]\s*(.*?)\s*$", line)
            if m and not line.lstrip().startswith(("#", "!")):
                props[m.group(1)] = m.group(2)
    return props


def version_from_properties(props):
    """(versionCode, versionName) from the VERSION_* convention, or (None, None)."""
    code = props.get("VERSION_CODE")
    parts = [props.get(k) for k in ("VERSION_MAJOR", "VERSION_MINOR", "VERSION_PATCH")]
    name = ".".join(parts) if all(parts) else props.get("VERSION_NAME")
    return code, name


def release_block(build):
    """Every release block, brace-matched and joined. A fixed-length slice read the debug block.

    shortcut: counts braces without tracking strings or comments, so a `{` inside a Gradle string
    literal inside a release block would end it early; upgrade to a real parse if that shows up.
    """
    out = []
    for m in re.finditer(r'(?:getByName|create)\("release"\)|\brelease\s*\{', build):
        start = build.find("{", m.start())
        if start < 0:
            continue
        depth = 0
        for i in range(start, len(build)):
            if build[i] == "{":
                depth += 1
            elif build[i] == "}":
                depth -= 1
                if depth == 0:
                    out.append(build[start:i + 1])
                    break
        else:
            out.append(build[start:])  # unbalanced braces: read to the end rather than drop the block
    return "\n".join(out)


def tracked_files(repo):
    """Files git tracks in repo, or None if it is not a git repo."""
    try:
        p = subprocess.run(["git", "-C", str(repo), "ls-files"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return p.stdout.splitlines() if p.returncode == 0 else None


def git_state(repo):
    try:
        branch = subprocess.run(["git", "-C", str(repo), "rev-parse", "--abbrev-ref", "HEAD"],
                                capture_output=True, text=True, timeout=30)
        dirty = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"],
                               capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None, None
    if branch.returncode != 0:
        return None, None
    return branch.stdout.strip(), len([l for l in dirty.stdout.splitlines() if l.strip()])


def audit_app(repo, min_target=None, tracked=tracked_files, git=git_state):
    repo = Path(repo)
    build_path = repo / "app" / "build.gradle.kts"
    if not build_path.is_file():
        build_path = repo / "app" / "build.gradle"
    build, catalog = read(build_path), catalog_versions(repo)
    release = release_block(build)
    prop_code, prop_name = version_from_properties(build_properties(repo, build))
    row = {
        "app": repo.name,
        "path": str(repo),
        "versionCode": value(build, catalog, "versionCode") or prop_code,
        "versionName": value(build, catalog, "versionName") or prop_name,
        "minSdk": value(build, catalog, "minSdk", "minSdkVersion"),
        "targetSdk": value(build, catalog, "targetSdk", "targetSdkVersion"),
        "compileSdk": value(build, catalog, "compileSdk", "compileSdkVersion"),
        "agp": catalog.get("agp") or catalog.get("androidGradlePlugin"),
        "kotlin": catalog.get("kotlin"),
        # Any assignment counts: signingConfigs.getByName(...) directly, or a variable holding it.
        "releaseSigning": bool(re.search(r"\bsigningConfig\s*(=\s*|\s+)\w", release)),
        "minify": bool(re.search(r"(isMinifyEnabled\s*=\s*true|minifyEnabled\s*=?\s*true)", release)),
        "issues": [],
    }
    files = tracked(repo)
    keys = [f for f in files or [] if any(Path(f).match(p) for p in KEY_PATTERNS)]
    row["branch"], row["uncommitted"] = git(repo)
    issues = row["issues"]
    # Only a literal assigned straight to the setting; not the key name inside getProperty("...").
    if re.search(r'(?<!["\w])(storePassword|keyPassword)\s*(?:=\s*|\s+)"[^"$]+"', build):
        issues.append("password written in the build file")
    if keys:
        issues.append("signing files tracked by git: " + ", ".join(keys))
    if not row["releaseSigning"]:
        issues.append("release build has no signingConfig")
    if not row["minify"]:
        issues.append("release build does not enable minify (R8)")
    if row["targetSdk"] is None:
        issues.append("targetSdk not found")
    elif min_target and row["targetSdk"].isdigit() and int(row["targetSdk"]) < min_target:
        issues.append(f"targetSdk {row['targetSdk']} is below {min_target}")
    if row["versionCode"] is None:
        issues.append("versionCode not found")
    if files is None:
        issues.append("not a git repository")
    return row


def table(rows):
    head = ["App", "versionName (code)", "min/target/compile", "AGP", "Kotlin", "Signing", "R8", "Git", "Issues"]
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for r in rows:
        git = "-" if r["branch"] is None else f"{r['branch']}" + (f", {r['uncommitted']} changed" if r["uncommitted"] else "")
        out.append("| " + " | ".join([
            r["app"], f"{r['versionName'] or '?'} ({r['versionCode'] or '?'})",
            f"{r['minSdk'] or '?'}/{r['targetSdk'] or '?'}/{r['compileSdk'] or '?'}",
            r["agp"] or "-", r["kotlin"] or "-", "yes" if r["releaseSigning"] else "NO",
            "yes" if r["minify"] else "NO", git, str(len(r["issues"])),
        ]) + " |")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root")
    ap.add_argument("--min-target", type=int)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if not Path(a.root).is_dir():
        print(f"not a folder: {a.root}", file=sys.stderr)
        return 2
    rows = [audit_app(r, a.min_target) for r in find_apps(a.root)]
    if a.json:
        print(json.dumps(rows, indent=2))
        return 0
    if not rows:
        print(f"no Android apps (app/build.gradle or app/build.gradle.kts) under {a.root}")
        return 0
    print(table(rows))
    issues = [(r["app"], i) for r in rows for i in r["issues"]]
    print(f"\n{len(rows)} apps, {len(issues)} issues" + (f" (targetSdk floor {a.min_target})" if a.min_target else
                                                         " (no targetSdk floor given)"))
    for app, issue in issues:
        print(f"- {app}: {issue}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
