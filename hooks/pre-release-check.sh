#!/usr/bin/env bash
# DroidForge PreToolUse(Bash) hook: warn before an Android release build or signing step.
# Warn only, never block: every path exits 0. Never reads or prints passwords.

input=$(cat)

if command -v jq >/dev/null 2>&1; then
  cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null)
elif command -v python3 >/dev/null 2>&1; then
  cmd=$(printf '%s' "$input" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))' 2>/dev/null)
else
  # shortcut: sed pulls the last "command" string out of the JSON; escaped quotes stay escaped. Fine for matching.
  cmd=$(printf '%s' "$input" | sed -nE 's/.*"command"[[:space:]]*:[[:space:]]*"(([^"\\]|\\.)*)".*/\1/p')
fi

# Fire only when gradle(w) runs a *Release bundle/assemble task, or a signer runs as a command,
# so "grep bundleRelease docs/" or "echo apksigner" do not trigger it.
start='(^|[;&|(][[:space:]]*)([^[:space:];&|]*/)?'
printf '%s' "$cmd" | grep -Eq "${start}gradlew?[[:space:]][^;&|]*(bundle|assemble)[A-Za-z0-9]*Release|${start}(apksigner|jarsigner)([[:space:]]|\$)" || exit 0

root=${CLAUDE_PROJECT_DIR:-$PWD}
cd "$root" 2>/dev/null || exit 0

warnings=()
warn() { warnings+=("$1"); }

gradle=""
for f in app/build.gradle.kts app/build.gradle; do
  [ -f "$f" ] && { gradle=$f; break; }
done

version_code() { grep -Eo 'versionCode[[:space:]]*=?[[:space:]]*[0-9]+' | head -n 1 | grep -Eo '[0-9]+$'; }

in_git=false
git rev-parse --is-inside-work-tree >/dev/null 2>&1 && in_git=true

if [ -z "$gradle" ]; then
  warn "No app/build.gradle.kts or app/build.gradle found in $root"
else
  current=$(version_code <"$gradle")
  if [ -z "$current" ]; then
    # A non-literal versionCode (e.g. from libs.versions.toml) cannot be compared; only warn when it is absent.
    grep -q 'versionCode' "$gradle" || warn "versionCode missing in $gradle. Run /droidforge:version-bump to set it."
  elif $in_git; then
    tag=$(git describe --tags --abbrev=0 2>/dev/null)
    if [ -n "$tag" ]; then
      tagged=$(git show "$tag:$gradle" 2>/dev/null | version_code)
      if [ -n "$tagged" ] && [ "$current" -le "$tagged" ]; then
        warn "versionCode $current is not greater than $tagged at tag $tag. Run /droidforge:version-bump."
      fi
    fi
  fi
  grep -q 'versionName' "$gradle" || warn "versionName missing in $gradle. Run /droidforge:version-bump to set it."
  grep -q 'signingConfigs' "$gradle" || warn "No signingConfigs block in $gradle. Run /droidforge:signing-config to generate one."
fi

# Only the KEYSTORE_PATH line is read; the password lines in local.properties are never touched.
if [ -f local.properties ]; then
  ks=$(grep -E '^[[:space:]]*KEYSTORE_PATH[[:space:]]*=' local.properties | head -n 1 | cut -d= -f2- | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
  if [ -n "$ks" ]; then
    # storeFile = file(...) resolves relative to app/, so accept the path from either directory.
    [ -f "$ks" ] || [ -f "app/$ks" ] || warn "Keystore file not found: $ks. Run /droidforge:keystore to generate it."
  fi
fi

if $in_git; then
  tracked=$(git ls-files -- '*.jks' '*.keystore' | paste -sd ' ' -)
  [ -n "$tracked" ] && warn "Keystore tracked by git: $tracked. Untrack it with git rm --cached; treat the key as exposed if it was pushed."
fi

for pat in jks keystore; do
  grep -Eqs "^[[:space:]]*(/|\*\*/)?\*\.$pat[[:space:]]*\$" .gitignore || warn "*.$pat is not in .gitignore. Add it so keystores are never committed."
done

[ ${#warnings[@]} -eq 0 ] && exit 0

msg="DroidForge pre-release check:"
for w in "${warnings[@]}"; do msg+=$'\n'"  - $w"; done

printf '%s\n' "$msg" >&2
# systemMessage is how a PreToolUse hook shows text to the user at exit 0; stderr alone is only visible in verbose mode.
if command -v jq >/dev/null 2>&1; then
  jq -n --arg m "$msg" '{systemMessage: $m}'
elif command -v python3 >/dev/null 2>&1; then
  python3 -c 'import json,sys; print(json.dumps({"systemMessage": sys.argv[1]}))' "$msg"
fi
exit 0
