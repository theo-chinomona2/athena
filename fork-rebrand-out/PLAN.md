# Athena by Sentio Langley — Rebrand Plan

**Stage:** 2 of fork-rebrand-pipeline
**Date:** 2026-06-19
**Source fork:** NousResearch/hermes-agent (MIT)
**Target product:** Athena — a Sentio Langley product

---

## New Identity

| Field | Value |
|---|---|
| Product name | **Athena** |
| Company | **Sentio Langley** |
| CLI binary | `athena` |
| PyPI package | `athena-agent` |
| Desktop app name | `Athena` |
| macOS/Windows bundle ID | `com.sentiolangley.athena` |
| Default home dir (Unix) | `~/.athena` |
| Default home dir (Windows) | `%LOCALAPPDATA%\athena` |
| Primary env var | `ATHENA_HOME` (falls back to `HERMES_HOME`) |
| Docker image | `sentiolangley/athena` |
| Docs URL | `athena.sentiolangley.me` ← **confirm before Stage 3** |
| Support email | `support@sentiolangley.com` ← **confirm before Stage 3** |
| GitHub repo | `theo-chinomona2/athena` ← **confirm rename intent** |
| Copyright line to add | `Copyright (c) 2026 Theo Chinomona / Sentio Langley` |

### What is NOT being renamed (upstream cherry-pick safety)

The following internal namespaces are **deliberately kept as-is**. Renaming them
would cause every upstream patch to conflict on import lines, destroying the
ability to cherry-pick security fixes.

- Python packages: `hermes_cli`, `hermes_state`, `hermes_constants`, `hermes_logging`, `hermes_bootstrap`, `hermes_time`
- npm packages: `@hermes/ink`, `@hermes/shared`, `@hermes/bootstrap-installer`
- Session key prefix: `agent:` (generic, not a brand name, baked into SQLite)
- `HERMES_HOME` env var: kept as the internal fallback; `ATHENA_HOME` is the new primary

Users never see these. They see the binary name, docs, desktop app name, and banner.

---

## Upstream-Merge Strategy

After each commit group, cherry-picks from upstream work on files this group did
NOT touch. Files this group DID touch require a manual conflict review — but those
are intentional divergences.

```
git fetch upstream
git cherry-pick <sha>   # conflicts only on files in this plan's groups
```

Files rated **LOW** below can be cherry-picked almost automatically.
Files rated **HIGH** (e.g. hermes_constants.py, run_agent.py) already have your
multi-tenant changes, so they'd conflict on upstream pulls regardless.

---

## Commit Groups (dependency order)

```
Group A  ──────────────────────────────────┐
  (foundation: binary name + home dir)     │
         ├──► Group C  (source strings)    │
         └──► Group D  (desktop + CI)      │
                                           │
Group B  (docs site)  ─────────────────────┤  all independent of each other
Group E  (locales)    ─────────────────────┤
Group F  (plugins)    ─────────────────────┘
```

Groups B, C, D, E, F can all execute in parallel after Group A lands.

---

## Group A — Foundation (do first, blocks C and D)

**Branch:** `rebrand/athena`
**Upstream-merge risk:** LOW-MEDIUM (2 files already diverged from upstream)

### A1: `pyproject.toml` — package metadata + binary name

```diff
-name = "hermes-agent"
+name = "athena-agent"

-authors = [{ name = "Nous Research" }]
+authors = [{ name = "Sentio Langley" }]

-hermes = "hermes_cli.main:main"
+athena = "hermes_cli.main:main"

-hermes-agent = "run_agent:main"
+athena-agent = "run_agent:main"

-hermes-acp = "acp_adapter.entry:main"
+athena-acp = "acp_adapter.entry:main"
```

Note: `py-modules` and `setuptools.packages.find` entries keep `hermes_*` names.

**Commit message:** `rebrand(pkg): rename binary to athena, package to athena-agent`

---

### A2: `hermes_constants.py` — ATHENA_HOME alias + default dir

In `get_hermes_home()` (line 73), before reading `HERMES_HOME`, check `ATHENA_HOME`:

```python
# Check ATHENA_HOME first; fall back to HERMES_HOME for compatibility.
val = os.environ.get("ATHENA_HOME", "").strip() or os.environ.get("HERMES_HOME", "").strip()
```

In `_get_platform_default_hermes_home()` (line 44):

```python
def _get_platform_default_hermes_home() -> Path:
    if sys.platform == "win32":
        local_appdata = os.environ.get("LOCALAPPDATA", "").strip()
        base = Path(local_appdata) if local_appdata else Path.home() / "AppData" / "Local"
        return base / "athena"
    return Path.home() / ".athena"
```

Update the docstring on `get_hermes_home()`:
- Change all references to `HERMES_HOME` in the docstring to `ATHENA_HOME / HERMES_HOME`
- Update the issue URL comment (line 67) to your own repo

**Commit message:** `rebrand(home): ATHENA_HOME env var + ~/.athena default dir; HERMES_HOME still works as fallback`

---

### A3: `LICENSE` — append Sentio Langley copyright

After the existing Nous Research copyright line, add:

```
Copyright (c) 2026 Theo Chinomona / Sentio Langley
```

Do NOT remove or replace the Nous Research line — MIT requires it.

**Commit message:** `rebrand(license): append Sentio Langley copyright`

---

### A4: `hermes_cli/banner.py` — repo URL, update check, ASCII art

Lines to change:

```python
# line 124 — update check source
_UPSTREAM_REPO_URL = "https://github.com/theo-chinomona2/athena.git"
_OFFICIAL_REPO_CANONICAL = "github.com/theo-chinomona2/athena"

# line 430 — release link
_RELEASE_URL_BASE = "https://github.com/theo-chinomona2/athena/releases/tag"

# line 235 — PyPI update check
def _fetch_pypi_latest(package: str = "athena-agent") -> ...:

# lines 64–120 — ASCII art
# Replace HERMES_AGENT_LOGO with ATHENA_LOGO (new art or remove)
# Replace HERMES_CADUCEUS with your own symbol or None
```

For the ASCII art, simplest options:
- Replace with `ATHENA` spelled out in the same block-letter style
- Or set `ATHENA_LOGO = None` and skip the art display (clean minimal banner)

**Commit message:** `rebrand(banner): update repo URLs, update-check package name, ASCII art`

---

## Group B — Docs Site (parallel with A)

**Branch:** `rebrand/athena`
**Upstream-merge risk:** LOW (docs/ rarely touched by upstream feature patches)

### B1: `website/docusaurus.config.ts`

Full replacement values:

```typescript
title: 'Athena',
tagline: 'The self-improving AI agent by Sentio Langley',
favicon: 'img/favicon.ico',
url: 'https://athena.sentiolangley.me',
baseUrl: '/',
organizationName: 'theo-chinomona2',
projectName: 'athena',

// editUrl (line 93):
editUrl: 'https://github.com/theo-chinomona2/athena/edit/main/',

// Footer copyright (line 188):
copyright: `Copyright © ${new Date().getFullYear()} Sentio Langley. Built on Hermes Agent (MIT).`,
```

Remove or replace:
- `discord.gg/NousResearch` → your own Discord or remove
- `nousresearch.com` footer link → `sentiolangley.com`
- All `hermes-agent.nousresearch.com` nav links → `athena.sentiolangley.me`
- All `github.com/NousResearch/hermes-agent` links → `github.com/theo-chinomona2/athena`

**Commit message:** `rebrand(docs): Docusaurus config — Athena / Sentio Langley URLs and branding`

---

### B2: Visual assets — provide your own files

The following files need replacement. Place your brand assets at these paths:

| Path | Current | Needed |
|---|---|---|
| `website/static/img/logo.png` | Hermes logo | Athena logo (SVG preferred) |
| `website/static/img/favicon.ico` | Hermes favicon | Athena favicon |
| `website/static/img/favicon.svg` | Hermes favicon SVG | Athena favicon SVG |
| `website/static/img/favicon-16x16.png` | 16px | 16px Athena |
| `website/static/img/favicon-32x32.png` | 32px | 32px Athena |
| `website/static/img/apple-touch-icon.png` | Touch icon | Athena touch icon |
| `website/static/img/hermes-agent-banner.png` | Hero banner | Athena hero banner — rename to `athena-banner.png` |
| `website/static/img/nous-logo.png` | Nous logo | Remove or replace with Sentio Langley logo |

**Note:** Update `website/docusaurus.config.ts` favicon path and any `<img>` src in docs MDX files that reference `hermes-agent-banner.png`.

**Commit message:** `rebrand(assets): replace logos, favicons, hero banner with Athena brand assets`

---

### B3: `README.md` — full rewrite

Key replacements:

```markdown
# Before
# Hermes Agent ☤

# After
# Athena

> An AI agent platform by [Sentio Langley](https://sentiolangley.com)
```

Remove:
- Nous Research badges (lines 11–13)
- Nous Portal section (lines 89–100)
- All `hermes-agent.nousresearch.com` URLs → `athena.sentiolangley.me`
- All `github.com/NousResearch/hermes-agent` URLs → your repo
- `discord.gg/NousResearch` → your community link or remove

Install command (line 39):
```bash
curl -fsSL https://athena.sentiolangley.me/install.sh | sh
```

**Commit message:** `rebrand(readme): Athena product name, Sentio Langley attribution, new URLs`

---

### B4: `CONTRIBUTING.md`, `AGENTS.md`, `SECURITY.md`

- Replace "Hermes Agent" → "Athena" throughout
- Replace Discord/GitHub links
- `SECURITY.md`: update contact to `security@sentiolangley.com`

**Commit message:** `rebrand(docs): update CONTRIBUTING, AGENTS, SECURITY for Athena`

---

## Group C — Source Strings (after Group A)

**Branch:** `rebrand/athena`
**Upstream-merge risk:** LOW-MEDIUM

### C1: User-Agent strings

| File | Line | Change |
|---|---|---|
| `hermes_cli/model_catalog.py` | 80 | `"athena-cli/{version}"` |
| `hermes_cli/models.py` | 24 | `"athena-cli/{version}"` |
| `run_agent.py` | 229 | `"AthenaAgent/{version}"` |
| `gateway/platforms/feishu.py` | 3288 | `"Mozilla/5.0 (compatible; AthenaAgent/1.0)"` |
| `optional-skills/devops/watchers/scripts/watch_rss.py` | 91 | `"Athena-Watcher/1.0"` |
| `optional-skills/devops/watchers/scripts/watch_github.py` | 116 | `"Athena-Watcher/1.0"` |
| `optional-skills/research/osint-investigation/scripts/_http.py` | 16 | `"(+https://github.com/theo-chinomona2/athena;"` |

**Commit message:** `rebrand(ua): update User-Agent strings to Athena`

---

### C2: NousResearch host-match dead code

| File | Line | Action |
|---|---|---|
| `run_agent.py` | 4838 | Remove `base_url_host_matches(..., "nousresearch.com")` branch or replace with your inference host if applicable |
| `trajectory_compressor.py` | 440 | Same |
| `hermes_cli/model_catalog.py` | 65, 74 | Update catalog URL to `athena.sentiolangley.me/model-catalog.json` or your own CDN; update raw GitHub URL to `raw.githubusercontent.com/theo-chinomona2/athena/main/...` |

**Commit message:** `rebrand(src): remove NousResearch host checks; update catalog URLs`

---

### C3: Nous Portal modules — disable, don't delete

Do **not** delete `hermes_cli/nous_billing.py` etc. (upstream cherry-picks will conflict if you delete files they patch). Instead:

In `hermes_cli/portal_cli.py` (lines 29–31), update constants to point nowhere or your own portal:

```python
DEFAULT_PORTAL_URL = ""        # or your own portal
SUBSCRIPTION_URL = ""
DOCS_URL = "https://athena.sentiolangley.me/docs/"
```

In `plugins/model-providers/nous/plugin.yaml`, set `enabled: false` in the plugin manifest so it doesn't show up in `athena plugins list` by default.

**Commit message:** `rebrand(portal): disable Nous Portal plugin; update portal URL constants`

---

### C4: Remaining source strings

| File | Line | Change |
|---|---|---|
| `gateway/platforms/email.py` | 142–143 | `"vendor" "Sentio Langley"` + `"support-email" "support@sentiolangley.com"` |
| `gateway/platforms/telegram.py` | 2147 | `https://github.com/theo-chinomona2/athena/issues` |
| `optional-skills/devops/watchers/scripts/watch_github.py` | 9 | Update example repo in skill comment |
| `acp_registry/agent.json` | all | `"id": "athena-agent"`, `"name": "Athena"`, repo/website URLs |
| `setup.py` | 31 | `prefix="athena-agent-{kind}-"` |
| `hermes_cli/uninstall.py` | 870, 872 | `athena.sentiolangley.me/install.*` |
| `scripts/install.sh` | 9, 215, 473 | `athena.sentiolangley.me/install.sh`; `"An AI agent platform by Sentio Langley."` |
| `scripts/install.ps1` | 8, 95–96, 161, 163 | Same URLs; "Sentio Langley" copy |
| `hermes_cli/main.py` | 6488 | `"you may miss updates from theo-chinomona2/athena."` |
| `cli.py` | 3062 | Remove `"- Nous Research"` or replace with `"- Sentio Langley"` |
| `cli.py` | 5286 | Keep the model warning; only change `"Nous Research Hermes 3 & 4 models"` → `"Nous Research Hermes models"` (these are third-party model names, not your brand) |
| `cli.py` | 8832, 9116 | Remove payment copy if not using Nous Portal |

**Commit message:** `rebrand(src): remaining source string replacements — email vendor, URLs, install scripts`

---

## Group D — Desktop App + CI (after Group A)

**Branch:** `rebrand/athena`
**Upstream-merge risk:** LOW (CI files, build configs — upstream rarely conflicts here)

### D1: `apps/desktop/package.json` — Electron app identity

```json
"name": "athena",
"productName": "Athena",
"author": "Sentio Langley",
"appId": "com.sentiolangley.athena",
"executableName": "Athena",
"legalTrademarks": "Athena",
"maintainer": "Sentio Langley <support@sentiolangley.com>",
"artifactName": "Athena-${version}-${os}-${arch}.${ext}",
```

CFBundle keys (lines 190–194):
```json
"CFBundleDisplayName": "Athena",
"CFBundleExecutable": "Athena",
"CFBundleName": "Athena"
```

URL protocol handler (line 143):
```json
"name": "Athena Protocol"
```

Replace `apps/desktop/public/hermes.png`, `hermes-sprite.png`, `hermes-frames/` with Athena assets.
Replace `apps/desktop/assets/icon.png` with Athena icon.

**Commit message:** `rebrand(desktop): Electron app name, bundle ID, author → Athena / Sentio Langley`

---

### D2: `apps/bootstrap-installer/` — Tauri installer

`src-tauri/Cargo.toml`:
```toml
name = "athena-bootstrap"
description = "Athena Setup"
authors = ["Sentio Langley <info@sentiolangley.com>"]
# binary name:
name = "Athena-Setup"
```

`src-tauri/tauri.conf.json`:
```json
"productName": "Athena",
"identifier": "com.sentiolangley.athena.setup"
```

**Commit message:** `rebrand(installer): Tauri bootstrap → Athena branding`

---

### D3: Docker + CI

`docker-compose.yml`:
```yaml
image: athena-agent
container_name: athena
# volume:
~/.athena:/opt/data
```

`docker-compose.windows.yml` (line 14, 25):
```yaml
image: sentiolangley/athena:latest
```

`Dockerfile`:
```dockerfile
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/athena/.playwright
RUN useradd -u 10000 -m -d /opt/data athena
WORKDIR /opt/athena
# binary paths: /opt/athena/bin/athena
```

`.github/workflows/docker-publish.yml`:
```yaml
IMAGE_NAME: sentiolangley/athena
# repo guard:
if: github.repository == 'theo-chinomona2/athena'
# GHCR cache:
ghcr.io/theo-chinomona2/athena:buildcache-arm64
```

`.github/workflows/deploy-site.yml`: update deploy target to `athena.sentiolangley.me`.

**Commit message:** `rebrand(ci): Docker image → sentiolangley/athena; CI repo guards → theo-chinomona2/athena`

---

## Group E — Locales (parallel with B, C, D)

**Branch:** `rebrand/athena`
**Upstream-merge risk:** LOW-MEDIUM

### E1: `locales/en.yaml` — English source

Changes:
- `` `hermes gateway restart` `` → `` `athena gateway restart` `` (and all `hermes` CLI command references)
- `"📖 **Hermes Commands**"` → `"📖 **Athena Commands**"`
- `"Share these links with the Hermes team for support."` → `"Share these links with the Athena team for support."`
- `"Not logged into Nous Portal."` → Remove this line or replace with your own auth copy

```bash
# Find all CLI command references in en.yaml:
grep -n '`hermes ' locales/en.yaml
```

**Commit message:** `rebrand(locales): en.yaml — CLI command refs and product name → Athena`

### E2: Non-English locales — defer

Update the 15 non-English locale files only after the English copy is finalised. Flag for a translation pass — the command-name changes are mechanical but the product-name strings should match your localised identity.

---

## Group F — Plugin Author Fields (parallel)

**Branch:** `rebrand/athena`
**Upstream-merge risk:** LOW

### F1: Model provider plugin.yaml files

In every `plugins/model-providers/*/plugin.yaml`, change:
```yaml
author: Nous Research
# →
author: Sentio Langley
```

**Exception:** `plugins/security-guidance/plugin.yaml` line 4:
```yaml
# KEEP:
author: "Anthropic (patterns, Apache-2.0) / NousResearch (Hermes plugin port)"
# Change only to:
author: "Anthropic (patterns, Apache-2.0) / Sentio Langley (Athena port)"
```

**Commit message:** `rebrand(plugins): update plugin.yaml author fields to Sentio Langley`

---

## Dependency Graph

```
[A1 pyproject.toml]─┐
[A2 hermes_constants]┤
[A3 LICENSE]         ├──► all groups can proceed after A lands
[A4 banner.py]      ─┘

[B1 docusaurus.config]  ─┐
[B2 visual assets]        │  parallel after A
[B3 README]               │  (B2 blocks on you providing logo files)
[B4 CONTRIBUTING/AGENTS] ─┘

[C1 User-Agent strings]  ─┐
[C2 host-match dead code]  │
[C3 Nous Portal disable]   │  parallel after A
[C4 remaining strings]    ─┘

[D1 Electron desktop]    ─┐
[D2 Tauri installer]       │  parallel after A
[D3 Docker + CI]          ─┘

[E1 locales/en.yaml]     ─── parallel after A

[F1 plugin.yaml files]   ─── parallel, any time
```

---

## Assets You Need to Provide Before Stage 3

Stage 3 cannot complete Group B without these:

- [ ] `website/static/img/logo.png` — Athena logo (SVG + PNG)
- [ ] `website/static/img/favicon.ico` + `favicon.svg` + `favicon-16x16.png` + `favicon-32x32.png`
- [ ] `website/static/img/apple-touch-icon.png`
- [ ] `website/static/img/athena-banner.png` (hero image for docs site)
- [ ] `apps/desktop/public/athena.png` + desktop assets
- [ ] `apps/desktop/assets/icon.png`
- [ ] Confirm: docs URL (`athena.sentiolangley.me`)
- [ ] Confirm: support email (`support@sentiolangley.com`?)
- [ ] Confirm: GitHub repo rename (`hermes-agent` → `athena`?)

---

## Stage 3 Execution Order

Once you confirm the above and provide the assets:

1. Create branch: `git checkout -b rebrand/athena`
2. Execute Group A (foundation) — commit A1, A2, A3, A4
3. Execute Groups B, C, D, E, F in parallel (subagent-driven)
4. Build + lint check: `python -m pytest tests/ -x -q && cd website && npm run build`
5. Verify the rebrand with `superpowers:verification-before-completion`
6. Write `fork-rebrand-out/UPSTREAM_NOTES.md` — log which files diverged hard from upstream

**Do not merge `rebrand/athena` into `developer` until Stage 3 verification is green.**
