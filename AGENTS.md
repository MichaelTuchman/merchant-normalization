# AGENTS.md — Merchant Normalization

## Purpose
This repository implements merchant identity normalization as a standalone, downstream component of Finance Foundry. Finance Foundry handles multi-source ingestion and harmonization; this repository produces a separate, auditable merchant-mapping overlay.

## Data boundaries
- Never modify Finance Foundry source files, existing Athena views, raw records, or transaction exports.
- The intended input is Finance Foundry's `trans_export` Athena view. Do not assume its column names, types, uniqueness constraints, or AWS identifiers. Verify the contract before implementing the live adapter.
- Preserve original transaction descriptions, amounts, and other source fields exactly.
- Write normalization results separately in a reusable merchant-mapping table keyed by Finance Foundry's cleaned `description`. This is a mapping key, not a unique transaction identifier; multiple transactions with the same description must reuse the same approved merchant mapping.
- Do not commit actual transactions, account information, credentials, tokens, or other private financial data.

## Merchant normalization
- Keep transaction-description cleaning distinct from identification of the underlying merchant.
- Use deterministic, explainable matching rules for approved mappings.
- Fuzzy, heuristic, or model-generated matches are suggestions requiring review before approval.
- Preserve provenance: original description reference, proposed or approved merchant, method, rule/version, and review status.
- Label unknown or ambiguous cases unresolved; never invent a merchant.
- Rules and approvals must be versioned and reproducible; equal inputs under equal rules must yield equal outputs.

## Implementation principles
- Prefer a small Python package with a CLI and automated tests, unless an explicit project decision changes the language.
- Dry-run must be the default. Persistent writes, including S3 or Athena changes, require an explicit apply flag.
- Isolate AWS access in adapters; core matching logic and tests must run offline.
- Use synthetic test fixtures. Cover ambiguity, rule precedence, idempotence, and preservation of original records.
- Validate input schemas and description-key semantics. Repeated descriptions in transaction input are expected. Require at most one current approved merchant per description; fail explicitly on conflicting approvals. Define handling of missing or blank descriptions and preserve transaction row counts when applying mappings. A unique transaction identifier is not required for the merchant-mapping table.
- Keep dependencies minimal and configuration explicit.

## Codex operating instructions
- Read this document before making changes.
- Work in one small, reviewable milestone at a time.
- Report exact changed files, executed tests, results, and unresolved questions.
- Verify that files, commits, and integrations actually exist before claiming completion.
- Do not access production financial data, write to AWS, or approve proposed merchant mappings without authorization.

## First milestone
Document the input contract required from `trans_export` and the output overlay schema. Verify the cleaned `description` field and its stability, equality semantics, and handling of missing values. Define mapping uniqueness and version history separately from transaction identity. Do not invent the live schema or connect to AWS during this milestone.
