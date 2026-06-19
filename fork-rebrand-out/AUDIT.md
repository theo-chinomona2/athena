# Fork-Rebrand Audit

**Project:** hermes-agent (fork of NousResearch/hermes-agent)
**Audit date:** 2026-06-19
**Auditor:** fork-rebrand-auditor
**Fork owner:** Theo Chinomona (theo-chinomona2/hermes-agent)

---

## 1. License & Attribution

**License file:** `/LICENSE` (MIT, 14 lines)

```
MIT License

Copyright (c) 2025 Nous Research
```

MIT is one of the most permissive open-source licenses. The only mandatory
obligation is that **all copies or substantial portions of the Software must
include the copyright notice and permission notice** (LICENSE lines 3-14).
This means:

- You must keep the `LICENSE` file in the repository as-is (or append your own
  copyright line beneath Nous Research's). You may NOT replace it.
- You are free to change the product name, all user-facing strings, domain
  names, logos, package names, and CLI command names — none of these are
  covered by the MIT text.
- There is no NOTICE file and no CLA requirement. There is no TRADEMARKS file.
  The project ships no Apache-2.0 NOTICE obligation.
- "Nous Research" and "Hermes" are names/marks the team uses, but the MIT
  license itself does not grant or restrict trademark rights. The name "Hermes"
  is also a Greek-mythology generic term; there is no registered trademark
  claim found in the repository.
- There is no copyleft; you may build a proprietary managed service on top of
  this without disclosing your additions.

**What you must preserve:**
- `LICENSE` file content — keep Nous Research's copyright line intact.
- If you add your own copyright, append it: `Copyright (c) 2026 Theo Chinomona / <ProductCo>`.

**What you can change freely:**
Everything else: product name, CLI command name, domain, logos, env-var
prefixes, Python package name, npm package names, Docker image tag.

**Verdict:** PROCEED-WITH-CONDITIONS

Conditions:
1. Keep the existing `LICENSE` file unmodified (or append — never replace).
2. Do not claim that Nous Research endorses your product (standard MIT good
   practice; no separate non-endorsement clause is needed under MIT but is
   good hygiene).

---

## 2. Upstream Remote Status

```
origin    https://github.com/theo-chinomona2/hermes-agent.git (fetch)
origin    https://github.com/theo-chinomona2/hermes-agent.git (push)
upstream  https://github.com/NousResearch/hermes-agent.git (fetch)
upstream  https://github.com/NousResearch/hermes-agent.git (push)
```

**Working tree:** Six untracked paths under the home directory root (`.bash_profile`,
`.bashrc`, `.claude/`, `.gitconfig`, `.gitmodules`, `.idea`, `.profile`,
`.ripgreprc`, `.vscode`, `.zprofile`, `.zshrc`) plus `dev/` inside the repo.
These are OS/editor files accidentally visible because the working directory is
the user's home; none are staged. The repo itself is clean.

**Branch:** `developer` (not `main`). Recent commits are Theo's own
multi-tenant work, branched from upstream `main`.

**Assessment:** The setup is correct for a hard fork. `upstream` is configured,
`origin` points to Theo's GitHub fork, and `upstream` points to
`NousResearch/hermes-agent`. Running `git fetch upstream && git merge
upstream/main` will work cleanly today.

**Recommendation:** Because this is a hard fork with no intent to contribute
back, the `upstream` remote can be left as-is for cherry-pick access but does
not need active merging. If the team wants upstream security fixes, the standard
flow is `git fetch upstream && git cherry-pick <sha>`. Consider creating a
long-lived `upstream-tracking` branch to make upstream diffs easy to inspect
without polluting `main`.

---

## 3. Architecture Summary

- **Entry points:** `hermes_cli/main.py` (`hermes` CLI command); `run_agent.py`
  (`hermes-agent` command, core agent loop); `gateway/run.py` (messaging
  gateway supervisor); `tui_gateway/server.py` + `apps/desktop/` (desktop TUI
  shell, Electron/Node wrapper); `acp_adapter/entry.py` (`hermes-acp`, ACP
  server adapter).
- **Agent core (`agent/`, `run_agent.py`):** Stateful LLM conversation loop,
  tool dispatch, history compression (`trajectory_compressor.py`), multi-model
  provider abstraction, async streaming.
- **Gateway (`gateway/`):** Long-running process that multiplexes incoming
  messages from platform adapters into agent sessions. Session lifecycle in
  `gateway/session.py`. Tenancy isolation in `gateway/tenancy.py`.
- **Platform adapters (`gateway/platforms/`):** One file per messaging platform
  — WhatsApp Cloud, Telegram, Slack, Discord, Matrix, Signal, Feishu, DingTalk,
  WeChat/Wecom, QQBot, Email, Teams, BlueBubbles, and an HTTP API server.
- **CLI (`hermes_cli/`):** ~50 subcommand modules — model setup, profile
  management, gateway install, Kanban task board, Nous Portal auth/billing,
  skills management, dashboard web server, doctor, etc.
- **Skills / optional-skills:** Markdown-driven skill files loaded at runtime;
  no compiled code. Extension point for domain-specific agent capabilities.
- **Plugins (`plugins/`):** Python packages for model providers, memory
  backends, and feature plugins (achievements, security guidance). Discovered
  via `hermes_cli/plugins.py` using `plugin.yaml` manifests.
- **State (`hermes_state.py`):** SQLite `state.db` under `HERMES_HOME`. Stores
  conversation history, session registry, Kanban tasks.
- **Config root (`hermes_constants.py`):** Single source of truth for
  `HERMES_HOME` resolution (~200 distinct `HERMES_*` env vars reference it).
- **Build system:** Python (uv/setuptools + pyproject.toml); Node/npm workspaces
  for the TUI (`ui-tui/`), web dashboard (`web/`), desktop app
  (`apps/desktop/`), and bootstrap installer (`apps/bootstrap-installer/`,
  Tauri/Rust). Test runner: pytest.

---

## 4. Brand Touchpoints

### Package metadata

| File | Line | Original value | Replacement type |
|------|------|----------------|-----------------|
| `pyproject.toml` | 9 | `name = "hermes-agent"` | New package name |
| `pyproject.toml` | 21 | `authors = [{ name = "Nous Research" }]` | New author |
| `pyproject.toml` | 297 | `hermes = "hermes_cli.main:main"` (script entry point) | New CLI command name |
| `pyproject.toml` | 298 | `hermes-agent = "run_agent:main"` (script entry point) | New command name |
| `pyproject.toml` | 299 | `hermes-acp = "acp_adapter.entry:main"` (script entry point) | New command name |
| `pyproject.toml` | 302 | `py-modules` list contains `hermes_bootstrap`, `hermes_constants`, `hermes_state`, `hermes_time`, `hermes_logging` | New module names (high-risk — see Risk Flags) |
| `pyproject.toml` | 346 | `setuptools.packages.find` includes `hermes_cli`, `hermes_cli.*`, `tui_gateway`, `tui_gateway.*` | New package names |
| `package.json` | 2 | `"name": "hermes-agent"` | New package name |
| `package.json` | 27 | `"url": "git+https://github.com/NousResearch/Hermes-Agent.git"` | New repo URL |
| `package.json` | 31 | `"bugs": "https://github.com/NousResearch/Hermes-Agent/issues"` | New issues URL |
| `package.json` | 33 | `"homepage": "https://github.com/NousResearch/Hermes-Agent#readme"` | New homepage |
| `apps/desktop/package.json` | 2 | `"name": "hermes"` | New name |
| `apps/desktop/package.json` | 3 | `"productName": "Hermes"` | New product name |
| `apps/desktop/package.json` | 7 | `"author": "Nous Research"` | New author |
| `apps/desktop/package.json` | 138 | `"appId": "com.nousresearch.hermes"` | New app bundle ID |
| `apps/desktop/package.json` | 139 | `"productName": "Hermes"` | New product name |
| `apps/desktop/package.json` | 140 | `"executableName": "Hermes"` | New executable name |
| `apps/desktop/package.json` | 143 | `"name": "Hermes Protocol"` (URL protocol handler) | New protocol name |
| `apps/desktop/package.json` | 149 | `"artifactName": "Hermes-${version}-..."` | New artifact name |
| `apps/desktop/package.json` | 190–194 | `CFBundleDisplayName`, `CFBundleExecutable`, `CFBundleName` all "Hermes" | New bundle names |
| `apps/desktop/package.json` | 226 | `"legalTrademarks": "Hermes"` | New trademark string |
| `apps/desktop/package.json` | 235 | `"maintainer": "Nous Research <support@nousresearch.com>"` | New maintainer |
| `apps/bootstrap-installer/src-tauri/Cargo.toml` | 2 | `name = "hermes-bootstrap"` | New crate name |
| `apps/bootstrap-installer/src-tauri/Cargo.toml` | 4 | `description = "Hermes Setup …"` | New description |
| `apps/bootstrap-installer/src-tauri/Cargo.toml` | 5 | `authors = ["Nous Research <info@nousresearch.com>"]` | New author |
| `apps/bootstrap-installer/src-tauri/Cargo.toml` | 14 | `name = "Hermes-Setup"` (binary name) | New binary name |
| `apps/bootstrap-installer/src-tauri/tauri.conf.json` | 3 | `"productName": "Hermes"` | New product name |
| `apps/bootstrap-installer/src-tauri/tauri.conf.json` | 5 | `"identifier": "com.nousresearch.hermes.setup"` | New bundle ID |
| `acp_registry/agent.json` | 2 | `"id": "hermes-agent"` | New agent ID |
| `acp_registry/agent.json` | 3 | `"name": "Hermes Agent"` | New agent name |
| `acp_registry/agent.json` | 6 | `"repository": "https://github.com/NousResearch/hermes-agent"` | New repo URL |
| `acp_registry/agent.json` | 7 | `"website": "https://hermes-agent.nousresearch.com/..."` | New website URL |
| `acp_registry/agent.json` | 12 | `"package": "hermes-agent[acp]==0.16.0"` | New package ref |

### Visual assets

| File | Notes | Replacement type |
|------|-------|-----------------|
| `assets/banner.png` | README hero image — "Hermes Agent" branding | Replace with new banner |
| `apps/desktop/public/hermes.png` | Desktop app logo | Replace with new logo |
| `apps/desktop/public/hermes-sprite.png` | Desktop sprite sheet | Replace |
| `apps/desktop/public/hermes-frames/hermes-frame-4.png` | Animation frames | Replace |
| `apps/desktop/public/apple-touch-icon.png` | Touch icon | Replace |
| `apps/desktop/assets/icon.png` | Desktop app icon | Replace |
| `website/static/img/hermes-agent-banner.png` | Docs site hero | Replace |
| `website/static/img/nous-logo.png` | Nous Research logo in docs footer | Replace |
| `website/static/img/logo.png` | Docs site logo | Replace |
| `website/static/img/favicon.ico` | Docs site favicon | Replace |
| `website/static/img/favicon.svg` | Docs site favicon SVG | Replace |
| `website/static/img/favicon-16x16.png` | Docs site favicon 16px | Replace |
| `website/static/img/favicon-32x32.png` | Docs site favicon 32px | Replace |
| `website/static/img/apple-touch-icon.png` | Docs site touch icon | Replace |
| `web/public/favicon.ico` | Dashboard web app favicon | Replace |
| `acp_registry/icon.svg` | ACP registry icon | Replace |

### Copy and docs

| File | Line(s) | Original value | Replacement type |
|------|---------|----------------|-----------------|
| `README.md` | 2 | `alt="Hermes Agent"` in banner img | New alt text |
| `README.md` | 5 | `# Hermes Agent ☤` | New title |
| `README.md` | 7 | `hermes-agent.nousresearch.com` (2 occurrences) | New docs URL |
| `README.md` | 11 | `discord.gg/NousResearch` badge | Remove or replace with own Discord |
| `README.md` | 13 | `"Built by Nous Research"` badge | Replace with own attribution |
| `README.md` | 18 | `"built by Nous Research"` in copy | New copy |
| `README.md` | 20 | `Nous Portal` reference | Replace or leave as provider option |
| `README.md` | 39 | `curl .../hermes-agent.nousresearch.com/install.sh` | New install URL |
| `README.md` | 44 | `github.com/NousResearch/hermes-agent/issues` | New issues URL |
| `README.md` | 49 | `hermes-agent.nousresearch.com/install.ps1` | New install URL |
| `README.md` | 56 | `hermes-agent.nousresearch.com/docs/...` (Termux guide) | New docs URL |
| `README.md` | 83 | `hermes-agent.nousresearch.com/docs/` | New docs URL |
| `README.md` | 89–100 | Entire "Nous Portal" section | Remove or replace with own portal |
| `README.zh-CN.md` | throughout | Same references in Chinese | Same replacements |
| `README.ur-pk.md` | throughout | Same references in Urdu | Same replacements |
| `CONTRIBUTING.md` | 1, 3, 12 | "Hermes Agent" product references | New product name |
| `CONTRIBUTING.md` | 48 | `discord.gg/NousResearch` | Remove or replace |
| `AGENTS.md` | throughout | "Hermes Agent" references | New product name |
| `SECURITY.md` | throughout | Project references | Update |
| `website/docusaurus.config.ts` | 6 | `title: 'Hermes Agent'` | New title |
| `website/docusaurus.config.ts` | 10 | `url: 'https://hermes-agent.nousresearch.com'` | New docs URL |
| `website/docusaurus.config.ts` | 13 | `organizationName: 'NousResearch'` | New org name |
| `website/docusaurus.config.ts` | 14 | `projectName: 'hermes-agent'` | New project name |
| `website/docusaurus.config.ts` | 93 | `editUrl: 'https://github.com/NousResearch/hermes-agent/edit/...'` | New edit URL |
| `website/docusaurus.config.ts` | 134, 143, 182 | `hermes-agent.nousresearch.com` nav links | New URL |
| `website/docusaurus.config.ts` | 148, 175, 183 | `github.com/NousResearch/hermes-agent` links | New repo URL |
| `website/docusaurus.config.ts` | 153, 174 | `discord.gg/NousResearch` | Remove or replace |
| `website/docusaurus.config.ts` | 184 | `nousresearch.com` footer link | Remove or replace |
| `website/docusaurus.config.ts` | 188 | `Built by Nous Research · MIT License` copyright | New copyright (keep MIT) |
| `locales/en.yaml` | 117 | `"Share these links with the Hermes team for support."` | New team name |
| `locales/en.yaml` | 154 | `"📖 **Hermes Commands**"` | New product name |
| `locales/en.yaml` | 233 | `` `hermes gateway restart` `` command reference | New CLI command |
| `locales/en.yaml` | 354 | `"Not logged into Nous Portal."` | Replace or remove if not using Nous Portal |
| `locales/*.yaml` | throughout | All 16 locale files contain `hermes` CLI command references and most contain "Hermes" product name strings | Systematic find-and-replace per locale |

### Source-level identity

| File | Line(s) | Original value | Replacement type |
|------|---------|----------------|-----------------|
| `hermes_constants.py` | 16–17 | `_HERMES_HOME_OVERRIDE` ContextVar name | Internal only — rename optional |
| `hermes_constants.py` | 50 | `Path.home() / ".hermes"` (default home dir name) | New hidden dir name (e.g., `.yourproduct`) |
| `hermes_constants.py` | 49 | `base / "hermes"` (Windows AppData path) | New Windows path segment |
| `hermes_constants.py` | 67 | Issue URL `NousResearch/hermes-agent/issues/18594` in docstring | Leave (code comment) or update |
| `hermes_cli/banner.py` | 64 | `HERMES_AGENT_LOGO` ASCII art (spells "HERMES AGENT") | Replace with new art |
| `hermes_cli/banner.py` | 71 | `HERMES_CADUCEUS` ASCII caduceus symbol | Replace or remove |
| `hermes_cli/banner.py` | 124 | `_UPSTREAM_REPO_URL = "https://github.com/NousResearch/hermes-agent.git"` | New repo URL |
| `hermes_cli/banner.py` | 125 | `_OFFICIAL_REPO_CANONICAL = "github.com/nousresearch/hermes-agent"` | New canonical URL |
| `hermes_cli/banner.py` | 430 | `_RELEASE_URL_BASE = "https://github.com/NousResearch/hermes-agent/releases/tag"` | New releases URL |
| `hermes_cli/banner.py` | 235 | `_fetch_pypi_latest(package: str = "hermes-agent")` default arg | New PyPI package name |
| `hermes_cli/model_catalog.py` | 65 | `"https://hermes-agent.nousresearch.com/docs/api/model-catalog.json"` | New catalog URL |
| `hermes_cli/model_catalog.py` | 74 | `"https://raw.githubusercontent.com/NousResearch/hermes-agent/main/..."` | New raw GitHub URL |
| `hermes_cli/model_catalog.py` | 80 | `_HERMES_USER_AGENT = f"hermes-cli/{_HERMES_VERSION}"` | New User-Agent string |
| `hermes_cli/models.py` | 24 | `_HERMES_USER_AGENT = f"hermes-cli/{_HERMES_VERSION}"` | New User-Agent string |
| `hermes_cli/portal_cli.py` | 29 | `DEFAULT_PORTAL_URL = "https://portal.nousresearch.com"` | Own portal URL or remove |
| `hermes_cli/portal_cli.py` | 30 | `SUBSCRIPTION_URL = "https://portal.nousresearch.com/manage-subscription"` | Own URL or remove |
| `hermes_cli/portal_cli.py` | 31 | `DOCS_URL = "https://hermes-agent.nousresearch.com/docs/..."` | New docs URL |
| `hermes_cli/nous_billing.py` | 35 | `DEFAULT_PORTAL_BASE_URL = "https://portal.nousresearch.com"` | Own portal URL or remove |
| `hermes_cli/providers.py` | 55 | `base_url_override="https://inference-api.nousresearch.com/v1"` | Own inference URL or leave as provider config |
| `hermes_cli/main.py` | 6488 | `"you may miss updates from NousResearch/hermes-agent."` | New repo URL |
| `hermes_cli/uninstall.py` | 870, 872 | `hermes-agent.nousresearch.com/install.*` | New install URL |
| `run_agent.py` | 229 | `"User-Agent": f"HermesAgent/{_HERMES_VERSION}"` | New User-Agent |
| `run_agent.py` | 4838 | `base_url_host_matches(self._base_url_lower, "nousresearch.com")` | New host check or remove |
| `trajectory_compressor.py` | 440 | `base_url_host_matches(url, "nousresearch.com")` | Same as above |
| `gateway/platforms/email.py` | 142–143 | `'"vendor" "NousResearch"'` and `'"support-email" "noreply@nousresearch.com")'` | New vendor string and support email |
| `gateway/platforms/feishu.py` | 3288 | `"Mozilla/5.0 (compatible; HermesAgent/1.0)"` | New User-Agent |
| `gateway/platforms/telegram.py` | 2147 | `"https://github.com/NousResearch/hermes-agent/"` | New issues URL |
| `optional-skills/devops/watchers/scripts/watch_rss.py` | 91 | `"User-Agent": "Hermes-Watcher/1.0"` | New User-Agent |
| `optional-skills/devops/watchers/scripts/watch_github.py` | 116 | `"User-Agent": "Hermes-Watcher/1.0"` | New User-Agent |
| `optional-skills/devops/watchers/scripts/watch_github.py` | 9 | `--repo NousResearch/hermes-agent` in skill comment | Update example |
| `optional-skills/research/osint-investigation/scripts/_http.py` | 16 | `"(+https://github.com/NousResearch/hermes-agent;"` | New URL |
| `cli.py` | 3062 | `"- Nous Research"` displayed in UI | New attribution or remove |
| `cli.py` | 5286 | `"Nous Research Hermes 3 & 4 models are NOT agentic"` | Reword (model warning remains valid; brand reference is to NousResearch's LLMs, not the product) |
| `cli.py` | 8832, 9116 | `"you allow Nous Research to charge your card"` | Own payment copy or remove if not using Nous Portal |
| `setup.py` | 31 | `prefix=f"hermes-agent-{kind}-"` (temp dir prefix) | New prefix |

### Configuration and infrastructure

| File | Line(s) | Original value | Replacement type |
|------|---------|----------------|-----------------|
| `hermes_constants.py` | 50, 73, 95–100+ | `HERMES_HOME` env var name — used by ~200 call sites across the repo | Leave as `HERMES_HOME` or rename systematically (see Risk Flags) |
| `hermes_constants.py` | 174, 213 | `HERMES_OPTIONAL_MCPS`, `HERMES_OPTIONAL_SKILLS` | Rename if renaming HERMES_ prefix |
| `docker-compose.yml` | 32–33 | `image: hermes-agent`, `container_name: hermes` | New image/container name |
| `docker-compose.yml` | 37, 71 | `~/.hermes:/opt/data` volume mount | New local dir name |
| `docker-compose.yml` | 39–40, 73–74 | `HERMES_UID`, `HERMES_GID` | New env var names (or keep) |
| `docker-compose.windows.yml` | 14, 25 | `image: nousresearch/hermes-agent:latest` | New Docker Hub image |
| `Dockerfile` | 20 | `ENV PLAYWRIGHT_BROWSERS_PATH=/opt/hermes/.playwright` | New path |
| `Dockerfile` | 92 | `useradd -u 10000 -m -d /opt/data hermes` (username) | New OS username |
| `Dockerfile` | 108 | `WORKDIR /opt/hermes` | New workdir |
| `Dockerfile` | 206–209 | `/opt/hermes/bin/hermes` binary path | New binary path |
| `.github/workflows/docker-publish.yml` | 47 | `env: IMAGE_NAME: nousresearch/hermes-agent` | New Docker Hub org/image |
| `.github/workflows/docker-publish.yml` | 60, 65 | `if: github.repository == 'NousResearch/hermes-agent'` gates | Update to fork repo name |
| `.github/workflows/docker-publish.yml` | arm64 cache refs | `ghcr.io/nousresearch/hermes-agent:buildcache-arm64` | New GHCR image path |
| `.github/workflows/skills-index.yml` | throughout | Workflow references to upstream repo | Update |
| `.github/workflows/deploy-site.yml` | throughout | Site deploy to `hermes-agent.nousresearch.com` | New deploy target |
| `scripts/install.sh` | 9, 215, 473 | `hermes-agent.nousresearch.com` install URL; `"An open source AI agent by Nous Research."` | New URL and copy |
| `scripts/install.ps1` | 8, 95–96, 161, 163 | `hermes-agent.nousresearch.com`; `NousResearch/hermes-agent.git` repo URLs; "Nous Research" copy | New URLs and copy |

### Theme and design tokens

| File | Notes | Replacement type |
|------|-------|-----------------|
| `hermes_cli/banner.py` 64–120 | ASCII-art logo spells "HERMES AGENT" in gold; caduceus symbol | New ASCII art or remove |
| `ui-tui/src/banner.ts` | TUI startup banner — confirm content | Review and replace |

### Internal namespaces (high-caution)

| Namespace | Scope | Notes |
|-----------|-------|-------|
| `hermes_cli` Python package | ~50 modules | Main CLI package — renaming requires updating all `from hermes_cli.x import y` calls throughout the codebase (hundreds of call sites) |
| `hermes_constants` module | Imported by ~30 files at module level | High-churn rename |
| `hermes_state` module | Imported widely | High-churn rename |
| `hermes_logging` module | Imported widely | High-churn rename |
| `hermes_bootstrap` module | Imported as first import in `run_agent.py` | Rename in lockstep |
| `tui_gateway` Python package | ~6 modules | Rename with pyproject.toml update |
| `@hermes/ink` npm package | Used by `ui-tui/` across 10+ source files | Rename in `ui-tui/package.json` and all imports |
| `@hermes/shared` npm package | Used by `apps/desktop/` | Rename in workspace config |
| `@hermes/bootstrap-installer` npm package | `apps/bootstrap-installer` | Rename in workspace config |
| `plugins/hermes-achievements/` plugin dir | Plugin discovery uses directory name | Rename plugin dir and `plugin.yaml` |

### Plugin author fields (Nous Research attribution in plugin.yaml files)

Every model-provider plugin under `plugins/model-providers/*/plugin.yaml` has
`author: Nous Research`. These files are user-visible via `hermes plugins list`.
Affected files:

`plugins/model-providers/copilot/plugin.yaml`, `alibaba/plugin.yaml`,
`azure-foundry/plugin.yaml`, `gemini/plugin.yaml`, `gmi/plugin.yaml`,
`huggingface/plugin.yaml`, `openrouter/plugin.yaml`, `xiaomi/plugin.yaml`,
`bedrock/plugin.yaml`, `stepfun/plugin.yaml`, `kimi-coding/plugin.yaml`,
`nvidia/plugin.yaml`, `copilot-acp/plugin.yaml`, `anthropic/plugin.yaml`,
`minimax/plugin.yaml`, `ollama-cloud/plugin.yaml`, `openai-codex/plugin.yaml`,
`xai/plugin.yaml`, `novita/plugin.yaml`, `opencode-zen/plugin.yaml`,
`zai/plugin.yaml`, `nous/plugin.yaml`.

`plugins/security-guidance/plugin.yaml` line 4:
`author: "Anthropic (patterns, Apache-2.0) / NousResearch (Hermes plugin port)"` —
this one must retain the Anthropic attribution; only the NousResearch part may
be changed to your name.

---

## 5. Risk Flags

### RF-1: Session keys baked into persisted SQLite rows — MEDIUM severity

**Location:** `gateway/session.py` lines 655–683; `hermes_state.py` line 108
(default DB path `HERMES_HOME/state.db`).

Session keys have the form `agent:<agent_id>:<platform>:dm:<chat_id>`. The
prefix `agent:` is generic (not the product name), so this is **not a brand
issue**. However, the key schema is stored verbatim in `state.db`. If you ever
rename the `agent_id` segment (currently defaults to `"main.main.main"` in
gateway tenant contexts), existing rows will become orphaned and active sessions
will not resume correctly.

**Mitigation:** The session-key format is generic enough that it survives a
product rebrand without modification. Only rename it if you also write a SQLite
migration script. Do not change `agent_id` values without a matching DB
migration.

---

### RF-2: HERMES_* env var surface is enormous — MEDIUM severity

**Location:** ~200 distinct `HERMES_*` environment variable names (see full
list in Brand Touchpoints). These appear in documentation, Docker Compose files,
scripts, and customer deployment guides.

If you rename `HERMES_HOME` to `MYPRODUCT_HOME`, every existing deployment,
every ops runbook, and every Docker Compose file your customers use will break.
This is the single highest-friction rename in the whole repo.

**Recommendation:** Keep `HERMES_HOME` as the internal env var for all data
stored during this fork iteration. Rebrand only the user-visible name (product
name, docs, CLI command). Introduce `MYPRODUCT_HOME` as an alias in
`hermes_constants.py` that `HERMES_HOME` falls back to — this gives you a
migration path without a flag day.

---

### RF-3: Python module names are import-contract — HIGH severity (internal)

**Location:** `hermes_cli/`, `hermes_constants.py`, `hermes_state.py`,
`hermes_logging.py`, `hermes_bootstrap.py`, `hermes_time.py` are Python module
names imported by hundreds of call sites inside the repo (and potentially by
any third-party plugins or scripts a tenant has installed).

Renaming these modules will break every `from hermes_cli.x import y` statement.
You must either do a whole-repo search-and-replace (safe for your own fork, but
will conflict on every `git fetch upstream && git cherry-pick`) or keep the
Python module names as-is and only rename the user-visible CLI command.

**Recommendation for a hard fork:** Rename the modules in one large commit
early on, before you accumulate your own feature commits on top. The sooner you
do it, the smaller the ongoing merge-conflict surface with upstream cherry-picks.

---

### RF-4: @hermes/ink is a load-bearing internal library — LOW-MEDIUM severity

**Location:** `ui-tui/packages/hermes-ink/`, referenced from ~15 TUI source
files as `@hermes/ink`. It is a forked version of the `ink` terminal-UI
library; the `@hermes/` npm namespace is the internal monorepo scope.

Renaming this to `@yourproduct/ink` requires updating all imports in
`ui-tui/src/**/*.ts(x)`, the `ui-tui/package.json` workspace reference, and
the `package-lock.json`. Risk is low (local monorepo scope, not published to
npm), but it is tedious.

---

### RF-5: Nous Portal billing/auth is deeply wired — MEDIUM severity (business)

**Location:** `hermes_cli/nous_billing.py`, `hermes_cli/nous_account.py`,
`hermes_cli/nous_subscription.py`, `hermes_cli/portal_cli.py`,
`plugins/model-providers/nous/__init__.py`. These modules handle OAuth login to
`portal.nousresearch.com`, credit management, subscription enforcement, and the
`NOUS_API_KEY` credential.

If you do not plan to offer Nous Portal as a model provider to your tenants,
these modules can be disabled at the plugin level (`plugins/model-providers/nous/`)
without touching core code. If you plan to offer your own model portal, you
will need to replace the portal URLs and OAuth endpoints throughout these files.

**Mitigation:** The plugin system means you can simply remove or disable
`plugins/model-providers/nous/` from your managed deployment. The `hermes
portal` CLI subcommand is dispensable. The `NOUS_API_KEY` check in
`tests/conftest.py` can be removed or made conditional.

---

### RF-6: Docker image identity — LOW severity

**Location:** `.github/workflows/docker-publish.yml` line 47,
`docker-compose.windows.yml` lines 14 and 25.

The CI workflow is gated on `github.repository == 'NousResearch/hermes-agent'`
so it will not run on your fork without changes. The `docker-compose.windows.yml`
hardcodes `nousresearch/hermes-agent:latest`. Users pulling that image from
Docker Hub will get NousResearch's build, not yours.

**Mitigation:** Update `IMAGE_NAME` in the workflow to your Docker Hub org (e.g.,
`theochinomona/your-product`), update the `if:` repo guards, and replace the
`docker-compose.windows.yml` image reference.

---

### RF-7: Upstream URL detection logic suppresses banners on forks — LOW severity

**Location:** `hermes_cli/banner.py` lines 124–125, 430–439.

The code compares the current git remote against `_OFFICIAL_REPO_CANONICAL =
"github.com/nousresearch/hermes-agent"` to decide whether to show a release
link in the startup banner. On your fork, `origin` is `theo-chinomona2/...`,
so the upstream link is already suppressed. If you rebrand, update
`_UPSTREAM_REPO_URL` and `_OFFICIAL_REPO_CANONICAL` to your own repo so the
update-check logic works correctly.

---

### RF-8: Email IMAP vendor string hardcoded — LOW severity

**Location:** `gateway/platforms/email.py` lines 142–143.

The IMAP CLIENTINFO capability string announces `"vendor" "NousResearch"` and
`"support-email" "noreply@nousresearch.com"` to the IMAP server. This is
metadata visible to the email server operator in server logs. It should be
replaced with your product name and support address.

---

### RF-9: Hardcoded NousResearch inference API host in provider behavior — LOW severity

**Location:** `run_agent.py` line 4838, `trajectory_compressor.py` line 440.

Both files call `base_url_host_matches(..., "nousresearch.com")` to apply
special request-handling logic (e.g., specific header patterns or stream
behavior) when the base URL is Nous Research's inference endpoint. If you do
not route traffic through `inference-api.nousresearch.com`, these branches are
dead code and can be removed. If you run your own inference gateway, add a
host-match for it.

---

### RF-10: 16 locale files each contain Hermes brand strings — LOW severity

**Location:** `locales/en.yaml`, `af.yaml`, `de.yaml`, `es.yaml`, `fr.yaml`,
`ga.yaml`, `hu.yaml`, `it.yaml`, `ja.yaml`, `ko.yaml`, `pt.yaml`, `ru.yaml`,
`tr.yaml`, `uk.yaml`, `zh.yaml`, `zh-hant.yaml`.

Each locale file contains both CLI command references (`` `hermes gateway
restart` ``) and product name strings ("Hermes Commands", "Hermes Gateway
Status"). The CLI command references must be updated if you rename the binary.
The product-name strings are user-visible support text.

**Mitigation:** The English locale (`en.yaml`) is the source of truth; all
others are translations. Update English first, then translate the changed keys.
Only `en.yaml` line 354 ("Not logged into Nous Portal") contains a Nous-specific
feature reference.

---

### RF-11: No telemetry phone-home detected — INFO (positive)

A search for sentry, posthog, mixpanel, and segment returned no results. The
"telemetry" references in the codebase are all internal health-monitoring
counters (Kanban dispatcher, gateway health), not outbound analytics. There are
no call-home endpoints to disable.

---

## 6. Recommended Next Step

The rebrand is legally clear (MIT, proceed with copyright preservation) and
technically feasible, but it is large in scope. The highest-leverage sequencing
is:

1. **Namespace rename first (before more feature commits):** Rename Python
   packages (`hermes_cli` → `<yourproduct>_cli`, etc.) and npm packages
   (`@hermes/ink` → `@<yourproduct>/ink`) in a single atomic commit on a
   dedicated branch. This eliminates the largest ongoing merge-conflict surface
   with upstream cherry-picks.

2. **CLI command and PyPI name:** Change `pyproject.toml` `name`, `[project.scripts]`,
   and `package.json` `name` to your chosen product name. This changes what
   users type (`hermes` → `<yourcommand>`).

3. **HERMES_HOME strategy:** Decide before touching env vars. Recommended: add
   `YOURPRODUCT_HOME` as a primary env var in `hermes_constants.py`, falling
   back to `HERMES_HOME` for compatibility with existing deployments. Do not
   delete `HERMES_HOME` support.

4. **Nou Portal modules:** If you are not offering Nous Portal to tenants,
   simply disable `plugins/model-providers/nous/` and do not promote the `hermes
   portal` command in your docs. No code deletion required yet.

5. **Visual / copy:** Banner images, README, docs site, and locale files are
   safe to update at any point — they have no code-level impact.

The natural next step is to invoke Stage 2 of the `/fork-rebrand-pipeline`
(`--plan-only`) to convert this audit into a prioritised, atomic task list with
exact file paths and sed-equivalent replacement targets for each category above.
