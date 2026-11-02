
## Shared FEGO image skill (v1.3)
At image planning, missing-image review, interior realism or generation requests in this workflow, read `docs/FEGO_IMAGE_SKILL.md` and proactively resolve `fego-photorealistic-interior`. Do not wait for its exact name. Prefer host metadata, then verified local installation, then the canonical private GitHub source through the connected GitHub tool. Missing native registration is not proof that the source is unavailable.
Load and suggest the skill when relevant; render only within the user's authorized scope. Preserve this repository's authorship and approval rules; imagery routing does not start the product content pipeline for blog/category work. Honor the user's Drive storage instructions over legacy local output paths.

# FEGO category workflow

For category content work, read `.agents/skills/fego-category/SKILL.md` and follow its two human gates. This is a CATEGORY workflow, separate from the FEGO blog repository; do not inherit its Codex-first authorship policy.

The root agent is the coordinator and sole external writer (Drive, WordPress, Elementor, Rank Math). Delegate bounded work to category_research, category_framework, category_seo and category_qa using stable versioned input files. Subagents inherit the parent model; do not set model overrides. Research and framework may work before Gate 1. SEO optimization and deployment preparation wait for Gate 1. QA may review research before Gate 1, but final deployment QA runs after SEO. Run independent reads/reviews in parallel; serialize all edits to the same document/site. Subagents never approve for the human.

Codex-generated prose is only a FRAMEWORK for the user to edit with Gemini. Never treat that prose as publishable, and never bypass the Gemini handoff merely because access is unavailable. Wait for the user's confirmed returned version.

Gate 1 = human approves an identified content snapshot returned after Gemini editing. Gate 2 = human approves the concrete deployment snapshot (target, text, SEO, media, link styling and diff). Explicit advance authorization such as "Nội dung này đã duyệt; tối ưu SEO rồi đăng luôn" can cover Gate 2 within its stated scope; still prepare and QA the exact result and log that advance authorization before publishing. Never request redundant confirmation already supplied. Substantial prose/fact changes invalidate Gate 1; changed deployment files invalidate an ordinary Gate 2.

Use `scripts/workflow.py` to record approvals and check snapshot hashes before CMS writes. These are local audit checks, not proof of human identity or CMS success. Do not record approval without an actual user instruction. Never manufacture PASS results or write a live object just to test connection readiness.

Keep category runs, approvals, source exports, backups and reports under ignored `runs/<category-slug>/`. Never copy MCP authorization values, application passwords, login cookies or environment secrets into this repository, reports, example commands or chat. Reuse an already configured connection without printing it.

Only the coordinator can apply writes after the gates. For existing published Elementor documents, mutations may be staged in an autosave; explicitly publish the approved update and verify the public category URL. Do not mistake a successful tool response, local config edit, or preview token for a verified live result. Preview failure must be reported. Preserve target IDs, URLs, existing product grid, media attribution and unrelated settings.
