---
name: fego-category
description: Draft FEGO WooCommerce category content directly in Google Docs, generate needed images in the same pass, then deploy the user's Gemini-revised version to WordPress.
---

## Shared imagery routing

Read `references/shared-image-routing.md` at image planning or missing-image review, without waiting for the exact image skill name. Resolve the canonical image skill and preserve this workflow's authorship and publication scope. For category preparation, the user's request to create the draft and images authorizes rendering the planned images in the same pass; do not add an anchor approval round. This does not authorize WordPress changes.

# FEGO category coordinator

Read `references/workflow.md`, `references/seo-and-layout.md`, and `references/deployment.md`. User instructions override this workflow; preserve explicit earlier authorization. Communicate in Vietnamese. At first use, say you are using the FEGO category workflow.

## Required outcome

Create one editable Google Doc as the working draft and generate the needed images in the same preparation pass. First inspect the category's existing sections and reference designs; calculate the copy and image slots to fit that structure and set those rules at the start. This is a considered first draft, not a publish-ready final. The user reviews and rewrites it with Gemini; deploy the returned version to WordPress.

## Roles

Root owns state, human communication, sources, external writes and final verification. Use available multi-agent tooling with the configured category roles; pass immutable snapshots and request evidence-bearing reports. If custom roles are unavailable in the current chat, use ordinary subagents with the corresponding role instructions; state the fallback. Never claim roles are globally installed just because files exist.

- category_research: product/category facts, URLs, media provenance and uncertainties; no writes.
- category_framework: category section fit, copy plan and image mapping; no writes.
- category_seo: review the Gemini-returned draft for search metadata and implementation issues; preserve user wording; no writes.
- category_qa: independent evidence checks and final artifact review; no writes or human approval.

## Workflow and approval boundaries

1. **Prepare in one pass.** Inspect the current category template and section structure first. Research only relevant products and facts, calculate how the copy fits those sections, set heading/content/media rules, and create the Google Doc plus the necessary images together. No separate prose approval before drafting, no anchor approval between image renders, and no default gallery quota. Prefer verified product media where useful; generate images for concrete section needs.
2. **User/Gemini review.** Hand over the single working Doc and its mapped image assets. The user reviews and rewrites with Gemini. Do not operate Gemini on the user's behalf. Treat the returned Gemini version as the deployment source and preserve its wording; flag material factual uncertainty instead of silently changing copy.
3. **WordPress deployment.** When the user returns/directs the Gemini version for WordPress, proceed with that deployment without asking for another generic content or publish approval. Verify the exact category and content targets, back up existing values, preserve the live product grid and unrelated settings, upload only mapped assets, then verify public readback and render. Ask only when a material scope is ambiguous or the actual write target cannot be verified.

Use `scripts/workflow.py` for snapshots and audit where useful, but do not turn its legacy two-gate prompts into extra human approval requirements. It never calls the website. Do not claim this helper enforces tool permissions. Record actual user/Gemini source snapshots and deployment actions; do not manufacture approvals.

## Work product

Initialize `runs/<slug>/state.json`; use one Google Doc as the content master and a concise media manifest. Freeze the Gemini-returned source and deployment payload. Preserve HTML links, heading hierarchy, caption/alt and media mapping from returned documents; exclude internal notes. Mark generated scenes as illustrations in provenance; never call them real product/customer photos.

Before WordPress changes: verify the target, snapshot current values, then apply the requested category update and verify public readback/render. Finish with exact edits, actual status, category link, checks performed and any limitations. A live deployment failing required QA is `needs_attention`, never `complete`.
