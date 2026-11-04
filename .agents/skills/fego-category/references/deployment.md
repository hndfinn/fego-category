# Deployment and QA

## Connection

Reuse the configured Elementor MCP server. Discover tools/schemas per site/session. Verify actual initialization and tools/list, not only local config. Do not read/print or copy stored Authorization values into artifacts. If native tools are unavailable but an authorized transport exists, report the transport used and call MCP over it; do not claim native registration. Config saved in a cloud workspace is not config saved on the user's desktop.

WoodMart custom elements and header/theme controls are not automatically supported by Elementor MCP. Discover widget schemas; V3 and V4 support varies by server. Use supported V4 edits for category body, preserving existing content. Never convert a live category wholesale just to make an API work.

## Prepare

Store a manifest using `templates/deployment-manifest.json`. Include the Gemini-returned source and every intended payload/asset/report in `files`. Use real IDs, verified URLs, statuses and output paths. Never put credentials into any manifest. Store website backups separately under the ignored run directory.

`workflow.py prepare` verifies term ID + block ID against the run target, requires the Gemini source, `media-map.json` (every image has section, file, alt, provenance) and passing `qa-preflight.json` in the manifest, then snapshots the referenced file bytes. `record-backup` stores the pre-write backup for the same target; `check-deploy` re-verifies both immediately before external writes. The script is local and never performs website writes.

## Apply

1. Confirm the user returned the Gemini version and instructed WordPress deployment for this category.
2. Re-read target term, metadata, Elementor tree and page status. Compare with preparation baseline; if target identity is ambiguous, resolve it before writing.
3. Back up current values (`templates/backup.json`: term description, SEO, Elementor block tree, page status) and run `record-backup` + `check-deploy`. Upload only mapped assets with deduplication by hash/map when available. Assign captions and alt independently.
4. Update category intro via verified taxonomy endpoint and SEO through observed supported Rank Math/other SEO API. Do not assume an arbitrary meta key was saved; inspect live title/meta.
5. Update Elementor with fresh IDs. After build-composition, never reuse an older element tree for manage-elements: it can overwrite new content. Serialize writes.
6. Published documents may stage mutations in autosave. Publish/promote the requested changes, then read back live.
7. Never rename blocks, change template assignments, URL, stock, tracking or unrelated global styles without scope.

## Required QA record (`templates/live-qa.json`, then `record-live-qa`)

- Public category HTTP status and final URL.
- One template H1; no H1 inside body block.
- Short intro before grid, long guide below, no duplication or internal notes.
- Intended SEO title/meta, canonical and robots directives.
- Expected text, headings and links match the Gemini-returned source; destinations work.
- Image count, mapping, alt/caption and provenance match `media-map.json`; files use the delivered formats.
- Scoped link styling emitted; browser desktop/mobile visual QA if available.
- Pagination behavior and no unintentional content duplication.
- Actual published/draft state; caches checked if public readback disagrees.
- Check failures, exact limitations and recovery steps.

Preview HTTP 500 is a real failure to report. Do not label a deployment visually verified without opening it. If data verification succeeds but render cannot be verified, mark `needs_attention` and explain; do not silently retry publication or broaden to server/plugin repairs. Fix reversible changes within authorization; otherwise report the concrete blocked action.

## Existing context (historical, recheck before use)

- Decorative shelves: category `/danh-muc/ke-gia-sach/ke-trang-tri/`, taxonomy `product_cat`, term ID 167, body block 13358.
- Mirror source was `01-guong-v2.docx`, body block 13374; it did not receive the same full live category audit.
- These observations do not authorize future overwrites. Discover IDs from current brief/site; never use this context as a default write target.
