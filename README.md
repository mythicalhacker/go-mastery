# Go Mastery — Agent Skill

The definitive Go (Golang) development skill for AI coding agents. It produces production-grade, idiomatic, high-performance Go across any domain — APIs, CLIs, distributed systems, real-time apps, AI/ML infrastructure, data pipelines, and more — and actively corrects the pre-1.22 Go habits most models pick up during training.

- **Go baseline 1.22, features through 1.26** (current stable as of June 2026), updated February 2026.
- **One skill, 36 deep reference files** covering everyday topics *and* rarely-documented ones: eBPF, WASM/TinyGo, CGo, distributed systems, runtime internals, AI/ML, MCP/agents, low-level networking, supply-chain security, and cross-language migration guides.
- **`INDEX.md` topic router** — 200+ topics mapped to `file.md#anchor` so the agent loads only the reference it needs, on demand.

## Measured impact

This skill isn't *claimed* to help — it's measured, in a companion open benchmark,
[**go-mastery-evals**](https://github.com/mythicalhacker/go-mastery-evals). Identical prompts run *with* and
*without* the skill, graded by the Go toolchain itself (`go build` / `go vet` / `go test` /
`golangci-lint`) plus a hidden behavioral test the model never sees — no LLM-as-judge, no vibes.

Across **54 production-Go cases** (samples=5, agentic self-correct), injecting the skill lifts
correctness on **every model of two vendors, with zero in-domain regressions**:

- **Anthropic** — Haiku **+20.0 pp**, Sonnet **+16.7 pp**, Opus **+14.1 pp**
- **OpenAI** — GPT‑5.4‑nano **+26.3 pp**, GPT‑5.4‑mini **+20.7 pp**, GPT‑5.5 **+12.6 pp**

It also leads every other Go skill benchmarked — JetBrains `go-modern-guidelines`
(+6.7 / +5.2 / +4.5 pp, never behind on a single case) and the leading community-authored Go skill
(+6.3 pp) — and stays neutral out of its domain (do-no-harm). On strong models, where pass/fail
saturates, a deterministic quality score still shows the code is more idiomatic. Full methodology,
per-tier tables, head-to-heads, and reproduction:
**[go-mastery-evals/RESULTS.md](https://github.com/mythicalhacker/go-mastery-evals/blob/main/RESULTS.md)**.

## What's in here

```
go-mastery/
├── SKILL.md        # Entry point: core rules + a routing table (always loaded when the skill triggers)
├── INDEX.md        # 200+ topic → reference#anchor map for on-demand lookups
├── references/     # 36 deep-dive files, lazy-loaded as needed
├── .claude-plugin/ # Claude Code plugin + marketplace manifests
├── LICENSE         # MIT
├── README.md
└── .gitignore
```

`SKILL.md` carries the always-on essentials (philosophy, project layout, naming, errors, concurrency, interfaces, testing, an anti-patterns table, and library picks). Everything deeper lives in `references/` and is pulled in only when a task calls for it.

## Installation

This is a standard [Agent Skill](https://agentskills.io) (`SKILL.md` + lazy-loaded references), so it works across SKILL.md-compatible agents. Two ways in: **local** (works today, no publishing required) and **remote** (after you push this folder to a Git repo).

### Local install (works now)

Copy or symlink this `go-mastery/` folder into your agent's skills directory:

| Agent | Skills directory |
|---|---|
| Claude Code | `~/.claude/skills/go-mastery` (global) or `<project>/.claude/skills/go-mastery` |
| Cursor | `~/.cursor/skills/go-mastery` or `<project>/.cursor/skills/go-mastery` |
| GitHub Copilot | `~/.copilot/skills/go-mastery` or `<project>/.copilot/skills/go-mastery` |
| Codex / OpenCode | `~/.agents/skills/go-mastery` |
| Antigravity | `~/.antigravity/skills/go-mastery` |

```bash
# Example (Claude Code, global):
mkdir -p ~/.claude/skills
cp -r /path/to/go-mastery ~/.claude/skills/
# or symlink so updates here propagate automatically:
ln -s /path/to/go-mastery ~/.claude/skills/go-mastery
```

### Remote install (after publishing to Git)

Once this folder is pushed to a public repo, the universal [`skills`](https://skills.sh) CLI installs it into any supported agent:

```bash
npx skills add mythicalhacker/go-mastery
```

Gemini CLI users:

```bash
gemini extensions install https://github.com/mythicalhacker/go-mastery
```

### Marketplace install (Claude Code plugin)

This repo doubles as a Claude Code plugin marketplace. Add it once, then install:

```bash
/plugin marketplace add mythicalhacker/go-mastery
/plugin install go-mastery@go-mastery
```

### ChatGPT / OpenAI

ChatGPT doesn't consume `SKILL.md` skills natively. Use it one of these ways:

- **Codex CLI** — install locally via `~/.agents/skills/go-mastery` (see table above).
- **Custom GPT / Projects** — paste `SKILL.md` into the system instructions, and add the most relevant `references/*.md` as uploaded knowledge files.

## Versioning

The skill targets Go features up to **1.26**. When working in a repo, prefer the Go version declared in its `go.mod` over the skill's baseline, and never emit features newer than that target. See `references/modern-go.md` for the full 1.21→1.26 feature matrix and the "old → modern" replacements.

## License

MIT — see [LICENSE](LICENSE).
