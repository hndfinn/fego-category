# Workflow semantics

## Intake and research

Read the brief and existing run first. Resolve category URL, taxonomy ID and exact block ID with read-only tools; a block name is not reliable identity. Ask only for missing information that sources cannot provide. Keep HTML blocks, category taxonomy, product pages and SEO records distinct.

Inventory the public page, pagination and product assortment. Read only relevant connected Drive sources; inspect Word/Docs structure, hyperlinks, inline media and internal-note boundaries. Use original supplied web assets where available rather than embedded Word compatibility copies. Read the relevant connector skill when first used. Check MCP connectivity with read-only calls, not live writes; custom widgets need observed schema support, not assumptions.

Researcher records fact → source URL → observed date, uncertainty and image provenance. Do not copy claims such as waterproof, load capacity, stock or warranty across products. Never invent volume, rankings, tested performance or real-world customer examples.

## Draft → Gemini → WordPress

Create the first usable category draft directly in one Google Doc; do not stop at an outline or framework. Before drafting, inspect the current category design and section slots. Decide the content structure, factual rules, link conventions, and how many images each section actually needs. Generate the planned images in that same preparation pass; no anchor-approval round. Prefer existing verified product images when they explain the choice, and do not impose an image quota.

The user reviews and rewrites the working Doc with Gemini. Do not operate Gemini on the user's behalf. Once the user returns/directs that Gemini version for WordPress, use it as the source, preserving the user's wording and mapping the already prepared media. Do not add redundant content or publish approval gates. Flag unresolved material facts and request clarification only if necessary to avoid a wrong claim or wrong target.

Keep a source snapshot/hash for traceability. Fix only clear implementation issues such as malformed links, missing alt text, or layout breakage without rewriting the user's substance. Any proposed factual correction or substantial rewrite must be surfaced to the user.

## Deployment

Prepare and deploy the Gemini-returned version when the user's instruction covers putting it on WordPress. Verify the exact term and content target, back up existing values, preserve the product grid and unrelated settings, upload mapped media, update SEO only where supported, and verify API readback plus public rendering. If a target is unverified, resolve it through read-only inspection; ask only if it remains ambiguous. Do not use an old generic authorization to infer a new unrelated scope.

## State

`drafting → draft_ready → gemini_returned → deployment_prepared → backed_up → complete`

There are no approval states. `draft_ready` = Google Doc + section-mapped images delivered; `gemini_returned` = user handed over the Gemini version (record the actual message); `deployment_prepared` = target/block, media map and preparation QA pass; `backed_up` = current live values saved for this exact target; `complete` only after every live QA check passes. Any failed or unverified live check: `needs_attention` with reason and recovery. State snapshots live under ignored runs. The helper computes/validates hashes; it does not implement WordPress permissions.
