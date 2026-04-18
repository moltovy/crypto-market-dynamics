# State-of-the-Art Tooling Notes (as of 2026-04-15)

## Cursor Pro
- Pro is listed at $20/mo.
- Official materials emphasize agent workflows, planning, rules, MCPs, skills/hooks, and cloud/background agents.
- Cursor docs and blog emphasize planning before coding, saving plans, and using project rules to shape agent behavior.
- For this project, Cursor should be treated as the main engineering and orchestration surface. citeturn775470search1turn775470search4turn775470search5

## GPT-5.4 / Codex
- Official OpenAI materials say GPT-5.4 is available in ChatGPT, the API, and Codex.
- It is positioned as a frontier model for professional work with strong reasoning, coding, tool use, and native computer-use capabilities.
- OpenAI also states it supports up to 1M tokens of context in Codex / API contexts and is intended for long-horizon, tool-heavy workflows. citeturn364240search0turn364240search3

## Claude Opus 4.6
- Anthropic describes Opus 4.6 as improved for coding, agentic tasks, code review, debugging, and large-codebase reliability.
- Anthropic also says it has a 1M-token context window in beta on the Claude Platform.
- This makes it a strong candidate for lead reviewer or lead manager roles in code-heavy research workflows. citeturn364240search1

## Gemini 3.1 Pro and Google Antigravity
- Google says Gemini 3.1 Pro is designed for more complex tasks and is being rolled out across developer and consumer products.
- Google explicitly includes Antigravity in the rollout surfaces.
- Antigravity is best thought of as an agentic development environment with strong planning/orchestration potential. citeturn364240search2

## Working Interpretation for This Project
- GPT-5.4 Extra High is a strong choice for repo-wide execution and long-horizon implementation ownership.
- Claude Opus 4.6 is a strong choice for deep review, critique, debugging, and alternate implementation.
- Cursor Pro is the main operating environment.
- Grok 4.20 should be used as a specialist advisor on how to structure the project, prompts, and operating model.


Use this section as-is:

## LLM Research and Decision-Support Stack

We have access to multiple frontier research tools and want them used deliberately, not redundantly. The goal is to treat them as a **decision-support layer** for literature review, methodology selection, data-source evaluation, engineering choices, and project scoping — not as substitutes for judgment. Every important project decision should be stress-tested across models when the downside of being wrong is high. ([OpenAI][1])

### Available tools to leverage

We currently have access to:

* **OpenAI GPT-5.4 / Deep Research / Codex**
* **Perplexity Pro / Research**
* **Gemini Pro / Deep Research**
* **Grok 4.20 Expert**
* **Qwen deep-research-style tooling**
  The exact official product naming for “Qwen 3.5 Deep Research Advanced” was not clearly verifiable from first-party sources during this review, so it should be treated as a **Qwen-based research capability** rather than assumed under that exact official product name. Verified official Qwen sources do confirm the broader Qwen ecosystem, including Qwen3, Qwen3-Coder, Qwen-Agent, and terminal/code-agent tooling. ([GitHub][2])

### Role assignment by platform

**GPT-5.4 / Deep Research / Codex** should be treated as the primary tool for complex, long-horizon professional work: integrating literature, reasoning across many moving parts, drafting rigorous research plans, and managing code-heavy execution in Cursor/Codex. Official OpenAI materials describe GPT-5.4 as their most capable professional-work model, with improved deep web research, long-horizon tool use, strong coding performance, native computer use in Codex/API, and up to a 1M-token context window. ([OpenAI][1])

**Perplexity Pro** should be used as the fastest high-citation literature and source-discovery engine. Official Perplexity materials state that Pro includes extended access to Research/Deep Research, multiple frontier model backends, document upload support, code sandboxing, and a workflow designed for in-depth reports with many sources. That makes it especially useful for finding recent finance papers, SSRN/arXiv work, methodology precedents, and source triangulation. ([Perplexity AI][3])

**Gemini Pro / Deep Research** should be used when source flexibility and Google ecosystem integration matter most. Official Google support states that Gemini Deep Research can use Google Search by default, can incorporate other sources like Gmail and Drive, can accept uploaded files, and has model options/limits that vary by plan. That makes it useful for long-form synthesis, comparative literature scans, and workflows involving external files or Google-native context. ([Google Help][4])

**Grok 4.20 Expert** should be used for strong real-time search, reasoning, and alternative challenge-function analysis. Official xAI materials describe Grok 4 / 4.20 as having native tool use, real-time search, large context windows, and strong agentic/tool-calling capability. It is therefore well suited for pressure-testing research directions, cross-checking recent crypto/market developments, and acting as a skeptical second opinion on decisions made elsewhere. ([xAI][5])

**Qwen-based research tooling** should be used as a low-cost breadth engine and alternative reasoning source, especially for comparative research, code-agent experimentation, and open-source-agent workflows. Official Qwen sources confirm an ecosystem including Qwen3, Qwen3-Coder, Qwen-Agent, and terminal/code-agent tooling, which makes it potentially valuable as an auxiliary research and engineering assistant even if the exact “3.5 Deep Research Advanced” branding could not be verified. ([GitHub][2])

### How these tools should be used in this project

These tools should help answer questions such as:

* What are the most relevant finance and crypto papers published or circulated in the last few months?
* What methods are appearing repeatedly in current crypto market-structure, ETF, liquidity, spillover, and factor-evolution research?
* Which empirical designs look overused, weak, or easy to attack?
* Which data sources are credible, reproducible, and actually worth the engineering effort?
* Which factor definitions are economically meaningful versus redundant?
* Which model families are most defensible for our setting: rolling regressions, structural breaks, VAR/FEVD, connectedness, PCA, clustering, or selective ML for variable reduction and regime discovery?
* How should Cursor Pro, Codex/GPT-5.4, Claude Opus, Gemini, Grok, and other tools be assigned roles in a multi-model workflow?

### Decision protocol

The intended operating principle is:

1. Use one model to generate a recommendation.
2. Use at least one other model to critique it.
3. Use a third model when the question is high-stakes, recent, technical, or expensive to get wrong.
4. Prefer decisions that survive cross-model scrutiny, are supported by current sources, and remain consistent with professional standards in finance, statistics, engineering, and reproducible research. ([OpenAI][1])

### What we want the lead model to do

The lead model should explicitly optimize for:

* **research quality**
* **source credibility**
* **methodological defensibility**
* **engineering simplicity**
* **reproducibility**
* **clear role assignment across models/tools**
* **avoiding unnecessary complexity**
* **making current, evidence-based decisions as of April 15, 2026** ([OpenAI][1])

