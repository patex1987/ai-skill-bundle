# Requested Knowledge-Base Feedback

Read the vault's `AGENTS.md`, index, affected notes, and template before editing. Resolve the location through `PROGRAMMING_KB_DIR` (set by the user, read by the `programming-kb` skill). If no location is configured, ask for it rather than assuming a host-specific path. Preserve the KB skill's invocation policy.

1. Separate reusable knowledge from facts true only of the researched codebase. Keep repository-specific behavior in that repository's docs. Do not turn a proposed preference into a personal decision without the user's instruction.
2. Search for existing coverage and update affected generated notes surgically. Avoid creating a second article for an existing concept under a new name.
3. Identify an existing immutable raw source or add a new source record as required by the vault. Never rewrite existing `raw/` inputs. Record provenance, dates, URLs, scope, and whether a record is a summary or captured source; do not mislabel paraphrases as originals. Respect source copyright limits.
4. Create or update the source summary, then only the relevant concept/pattern pages and relationships. Preserve frontmatter conventions, created dates, and useful historical qualifications. Add updated dates and evidence. Unverified synthesis should not silently become stable guidance.
5. Resolve contradictions with explicit qualification or mark affected notes for review. Keep source statements distinct from synthesis and project choices.
6. Update `index.md`, related links, and append an entry to `log.md` in its established format. Check frontmatter, link targets, index coverage, and changed files. Summarize which notes changed and why.

Filesystem permission remains separate from task authorization. If the vault is outside writable roots, request the necessary tool escalation when permitted. If writing is unavailable, stage an exact proposed update in the authorized workspace and report that it has not been ingested. Do not claim a staged proposal is a completed wiki update.
