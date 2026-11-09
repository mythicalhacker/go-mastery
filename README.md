# Go Mastery — Agent Skill

The definitive Go (Golang) development skill for AI coding agents. It produces production-grade, idiomatic, high-performance Go across any domain — APIs, CLIs, distributed systems, real-time apps, AI/ML infrastructure, data pipelines, and more — and actively corrects the pre-1.22 Go habits most models pick up during training.

- **Go baseline 1.22, features through 1.26** (current stable as of June 2026), updated February 2026.
- **One skill, 36 deep reference files** covering everyday topics *and* rarely-documented ones: eBPF, WASM/TinyGo, CGo, distributed systems, runtime internals, AI/ML, MCP/agents, low-level networking, supply-chain security, and cross-language migration guides.
- **`INDEX.md` topic router** — 200+ topics mapped to `file.md#anchor` so the agent loads only the reference it needs, on demand.

## Measured impact

The benchmark compared six models on 54 Go tasks, with five samples per task in each condition.
Both groups received the same task prompt and could make up to two repairs using toolchain feedback.
The skill group also received `SKILL.md` and the references selected for that task. Hidden behavioral
tests counted toward the final grade. Their output was withheld during repairs.

The final sample pass rate increased on all six models:

- **Anthropic** — Haiku **+20.0 percentage points** (197/270 to 251/270), Sonnet **+16.7**, Opus **+14.1**.
- **OpenAI** — GPT‑5.4‑nano **+26.3 percentage points**, GPT‑5.4‑mini **+20.7**, GPT‑5.5 **+12.6**.

Seven model/task pairs had fewer passing samples with the skill. All pairs with at least three
of five samples passing without the skill still had at least three passing with it.

An earlier build scored 4.5 to 6.7 percentage points higher than JetBrains `go-modern-guidelines`
across three Claude models and 6.3 points higher than a community skill on Sonnet.
On the external Aider polyglot Go track (36 Exercism puzzles, 108 samples per model per condition),
Haiku passed 15 samples with the skill and 13 without. Sonnet passed 59 versus 60, and Opus 63
versus 64. [Full benchmark results](https://github.com/mythicalhacker/go-mastery-evals/blob/717d447b96215a05520365e9a21098c9ab687aa3/RESULTS.md) · [External sample grades](https://github.com/mythicalhacker/go-mastery-evals/blob/717d447b96215a05520365e9a21098c9ab687aa3/baselines/deepened-v2-aider/results.json)

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
