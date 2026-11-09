# AGENTS.md — Merchant Normalization

## Purpose
This repository implements merchant identity normalization as a standalone, downstream component of Finance Foundry. Finance Foundry handles multi-source ingestion and harmonization; this repository produces a separate, auditable merchant-mapping overlay.

## Data boundaries
- Never modify Finance Foundry source files, existing Athena views, raw records, or transaction exports.
- The intended input is Finance Foundry's `trans_export` Athena view. Do not assume its column names, types, uniqueness constraints, or AWS identifiers. Verify the contract before implementing the live adapter.
- Preserve original transaction descriptions, amounts, and other source fields exactly.
- Write normalization results separately in a reusable merchant-mapping table keyed by Finance Foundry's cleaned `description`. This is a mapping key, not a unique transaction identifier; multiple transactions with the same description within the same effective period must reuse the same approved merchant mapping. The same description may resolve differently in different periods.
- Do not commit actual transactions, account information, credentials, tokens, or other private financial data.

## Merchant normalization
- Resolve each transaction description to the most recognizable business identity supported by evidence at the transaction date, using effective-dated mappings. A legal entity, franchise operator, or payment descriptor may map to a recognizable trading name or brand only when evidence supports that relationship for the applicable period.
- Match the cleaned `description` and select the approved mapping effective on `transaction_dt`. Use inclusive `effective_from` and exclusive `effective_to` dates; a missing end date means open-ended validity. Do not infer historical validity from present-day identity alone.
- Preserve evidence references and the period they support. Missing or invalid transaction dates, gaps in approved coverage, or insufficient identity evidence remain unresolved. Reject overlapping approved periods for the same description explicitly.
- Keep transaction-description cleaning distinct from identification of the underlying merchant.
- Use deterministic, explainable matching rules for approved mappings.
- Fuzzy, heuristic, or model-generated matches are suggestions requiring review before approval.
- Preserve provenance: original description reference, proposed or approved merchant, method, rule/version, review status, evidence references, and effective dates. Keep approval/revision history separate from the dates when a mapping applies to transactions.
- Label unknown or ambiguous cases unresolved; never invent a merchant.
- Rules and approvals must be versioned and reproducible; equal inputs under equal rules must yield equal outputs.

## Implementation principles
- Prefer a small Python package with a CLI and automated tests, unless an explicit project decision changes the language.
- Dry-run must be the default. Persistent writes, including S3 or Athena changes, require an explicit apply flag.
- Isolate AWS access in adapters; core matching logic and tests must run offline.
- Use synthetic test fixtures. Cover ambiguity, rule precedence, idempotence, preservation of original records, effective-date boundaries, gaps, overlapping approvals, and historical business identity changes.
- Validate input schemas and description-key semantics. Repeated descriptions in transaction input are expected. Require at most one applicable approved mapping per description and transaction date; reject overlapping approved periods and conflicting approvals. Define handling of missing or blank descriptions and preserve transaction row counts when applying mappings. A unique transaction identifier is not required for the merchant-mapping table.
- Keep dependencies minimal and configuration explicit.

## Codex operating instructions
- Read this document before making changes.
- Work in one small, reviewable milestone at a time.
- Report exact changed files, executed tests, results, and unresolved questions.
- Verify that files, commits, and integrations actually exist before claiming completion.
- Do not access production financial data, write to AWS, or approve proposed merchant mappings without authorization.

## First milestone
Document the input contract required from `trans_export` and the output overlay schema. Verify the cleaned `description` field and its stability, equality semantics, and handling of missing values. Define effective-dated mapping uniqueness, evidence provenance, and revision history separately from transaction identity. Do not invent the live schema or connect to AWS during this milestone.
