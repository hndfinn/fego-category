---
name: fego-category
description: Prepare and deploy FEGO WooCommerce category content with a mandatory user/Gemini editorial gate and a separate publish gate. Coordinate evidence, SEO, media, Elementor and live QA.
---

## Shared imagery routing

Read `references/shared-image-routing.md` at image planning or missing-image review, without waiting for the exact image skill name. Resolve the canonical image skill and preserve this workflow's authorship, content gates and publication scope. Loading/planning does not authorize rendering.

# FEGO category coordinator

Read `references/workflow.md`, `references/seo-and-layout.md`, and `references/deployment.md`. User instructions override this workflow; preserve explicit earlier authorization. Communicate in Vietnamese. At first use, say you are using the FEGO category workflow.

## Required outcome

Deliver a category introduction above the WooCommerce grid and an optional buying guide below it, with evidence-backed facts, natural keywords, accessible contextual links and appropriate images. Codex prose is a framework; the user edits with Gemini before optimizing or deploying it.

## Roles

Root owns state, human communication, sources, external writes and final verification. Use available multi-agent tooling with the configured category roles; pass immutable snapshots and request evidence-bearing reports. If custom roles are unavailable in the current chat, use ordinary subagents with the corresponding role instructions; state the fallback. Never claim roles are globally installed just because files exist.

- category_research: product/category facts, URLs, media provenance and uncertainties; no writes.
- category_framework: structure, user questions and Gemini handoff; no final authorship or writes.
- category_seo: only after Gate 1, proposed bounded changes to the approved version; no CMS writes.
- category_qa: independent evidence checks and final artifact review; no writes or human approval.

## Gates — exactly two human approval boundaries

1. **Gate 1: content approval.** Present the framework/Gemini handoff. Wait for the user's returned final content and explicit approval of that version. A Drive folder, reviewer PASS, image approval, instruction to research, or silence is not content approval. Ask once if required approval is missing. Record source snapshot/hash and the actual approving message.
2. **Gate 2: publish approval.** Prepare SEO, layout, links, image manifest and a concrete preview/local artifact plus diff first. Present only material changes. Wait for approval of that deployment snapshot before external staging or live writes, unless previous explicit authorization already covers staging/publish. A failed preview does not waive this gate: provide a complete local review bundle and disclose the limitation. Explicit "optimize and publish" after content approval may provide advance approval; log its scope, prepare and QA everything, then publish without asking again. Do not use a generic "làm đi" from an earlier research task as unlimited authorization.

Use `scripts/workflow.py` to record state and detect changed inputs. It never calls the website. Do not claim this helper enforces tool permissions; it is a required coordinator preflight. If source changes materially, reopen Gate 1. If the deployment package changes, reopen Gate 2 unless the actual user authorization explicitly covers those bounded changes.

## Work product

Initialize `runs/<slug>/state.json`; use templates for brief, Gemini handoff and manifest. Freeze research, approved text and deployment payloads. Preserve HTML links, heading hierarchy, caption/alt and media mapping from returned documents; exclude internal notes. Mark generated scenes as illustrations in provenance; never call them real product/customer photos.

After approval: back up objects, preflight target and hash checks, apply staged writes sequentially, publish when authorized, and verify the public category URL plus API readback. Finish with exact edits, actual status, link to category, checks performed and remaining limitations. A live deployment failing required QA is `needs_attention`, never `complete`.
