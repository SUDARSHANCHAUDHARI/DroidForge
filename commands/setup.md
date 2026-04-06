---
description: One-time DroidForge setup — saves your Android developer conventions to .claude-plugin-config.json so all commands work without repeated questions.
argument-hint: "[--update to overwrite existing config]"
allowed-tools: Read, Write, AskUserQuestion
---

Run one-time setup for DroidForge. Saves your Android developer conventions to `.claude-plugin-config.json` so all commands work without asking for your details every time.

## Steps

1. Check if `.claude-plugin-config.json` already exists in the current directory:
   - If it exists: read it, display the current config in a readable table, then ask "Update config? (y/n)". If user says n, stop.
   - If it does not exist: proceed with fresh setup.

2. Ask the user these questions one by one (do not ask all at once — wait for each answer):

   **Developer info**
   - "Your full name or developer display name:" (e.g. Jane Smith)
   - "Company or developer label:" (e.g. JaneTechLabs)
   - "GitHub username:" (e.g. janecoder)
   - "Country:" (e.g. United States)
   - "Country code — 2 letters for keystore:" (e.g. US, GB, IN, TH, AU)
   - "City:" (e.g. New York)

   **Android conventions**
   - "Package prefix — all your apps start with this:" (e.g. com.janecoder)
   - "Keystore password — choose a strong password, stored locally, never committed:" (use AskUserQuestion with type: password if supported, else plain text)
   - "Confirm keystore password:" (must match — if mismatch, ask again)

   **GitHub Pages**
   - "Privacy policy URL pattern — press Enter for default:" show the default as `https://[github_username].github.io/{appname}-privacy-policy/` substituting their entered github_username. Accept Enter to confirm default.

3. Write the following JSON to `.claude-plugin-config.json`:

```json
{
  "developer": {
    "name": "[answer]",
    "company": "[answer]",
    "github_username": "[answer]",
    "country": "[answer]",
    "country_code": "[answer]",
    "city": "[answer]"
  },
  "android": {
    "package_prefix": "[answer]",
    "keystore_password": "[answer]",
    "keystore_cn": "[company answer]",
    "keystore_country_code": "[country_code answer]",
    "keystore_city": "[city answer]"
  },
  "github_pages": {
    "privacy_policy_pattern": "https://[github_username].github.io/{appname}-privacy-policy/"
  },
  "plugin_version": "1.0.0",
  "configured_at": "[today's date in YYYY-MM-DD format]"
}
```

4. Check if `.gitignore` exists:
   - If it does not exist: create it with `.claude-plugin-config.json` as the first entry.
   - If it exists: read it and check if `.claude-plugin-config.json` is already listed. If not, append it on a new line.

5. Output the confirmation summary:

```
DROIDFORGE SETUP COMPLETE
──────────────────────────
Developer:      [name] ([company])
GitHub:         [github_username]
Package prefix: [package_prefix]
Keystore pass:  ••••••••• (saved locally)
Country:        [country] ([country_code])
City:           [city]

All DroidForge commands will now use these settings.
IMPORTANT: .claude-plugin-config.json is in your .gitignore — never commit it.
```
