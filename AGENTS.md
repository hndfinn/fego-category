
## Shared FEGO image skill routing (render v1.2)
At image planning, missing-image review, interior realism or generation requests in this workflow, read `docs/FEGO_IMAGE_SKILL.md` and proactively resolve `fego-photorealistic-interior`. Do not wait for its exact name. Prefer host metadata, then verified local installation, then the canonical private GitHub source through the connected GitHub tool. Missing native registration is not proof that the source is unavailable.
For category preparation, the user's request to create the draft authorizes rendering the planned section images in the same pass; do not add an anchor-approval round. Keep product fidelity, source checks and image QA. Preserve explicit no-generation or use-originals instructions. Imagery routing does not start the product content pipeline for blog/category work. Honor the user's Drive storage instructions over legacy local output paths.

# FEGO category workflow

For category content work, read `.agents/skills/fego-category/SKILL.md`. This is a CATEGORY workflow, separate from the FEGO blog repository; do not inherit its outline/approval policy.

Workflow (no intermediate approval gates):

1. **Draft + images in one pass.** Inspect the current category template/sections and reference category first, fix copy/heading/link/image rules, then create one editable Google Doc draft and generate the needed images together, mapped to sections. No outline/framework approval, no anchor approval, no image quota.
2. **User reviews and rewrites with Gemini.** Do not operate Gemini on the user's behalf. The returned Gemini version is the deployment source; preserve its wording.
3. **Deploy the Gemini version to WordPress** when the user directs it. Do not ask for another generic content or publish approval. Ask only if the target or a material scope is ambiguous after read-only inspection.

The root agent is the coordinator and sole external writer (Drive, WordPress, Elementor, Rank Math). Delegate bounded work to category_research, category_framework, category_seo and category_qa using stable versioned input files. Subagents inherit the parent model; do not set model overrides. Run independent reads/reviews in parallel; serialize all edits to the same document/site. Subagents never decide for the human.

Safeguards that remain mandatory (they are checks, not approval gates): verify the exact category (term ID) and content block ID with read-only tools; map every image to a section with alt/provenance; pass preparation QA; back up current term/SEO/block values immediately before writes; after publishing, verify API readback, public HTML and render. Use `scripts/workflow.py` (`record-gemini`, `prepare`, `record-backup`, `check-deploy`, `record-live-qa`) to snapshot and check these locally. They are local audit checks, not proof of CMS success. Never manufacture PASS results or write a live object just to test connection readiness.

Keep category runs, source exports, backups and reports under ignored `runs/<category-slug>/`. Never copy MCP authorization values, application passwords, login cookies or environment secrets into this repository, reports, example commands or chat. Reuse an already configured connection without printing it.

Only the coordinator applies writes. For existing published Elementor documents, mutations may be staged in an autosave; explicitly publish the update and verify the public category URL. Do not mistake a successful tool response, local config edit, or preview token for a verified live result. Preview failure must be reported. Preserve target IDs, URLs, existing product grid, media attribution and unrelated settings. A deployment failing required live QA is `needs_attention`, never `complete`.
