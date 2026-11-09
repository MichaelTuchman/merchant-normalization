# Merchant Normalization

Merchant Normalization is an independent, downstream component of Finance Foundry. Finance Foundry ingests and harmonizes transactions from multiple sources; Merchant Normalization is intended to identify the merchants represented in those transactions and produce a separate, auditable merchant-mapping overlay.

This repository contains an offline Python function for exact lookup against a caller-supplied approved mapping table. No live AWS adapter, fuzzy matching, AI matching, or approval workflow is implemented. The broader contracts below describe the intended application.

## Using the current lookup function

Requires Python 3.10 or later and no third-party dependencies. From the repository root:

```python
from merchant_normalization import normalize_merchant

# Synthetic example only; real tables must contain already-approved mappings.
approved_mappings = {"EXAMPLE CAFE CITY ZZ": "Example Cafe"}
result = normalize_merchant(
    "EXAMPLE CAFE CITY ZZ",
    approved_mappings,
    mapping_version="example-v1",
)
assert result.merchant_name == "Example Cafe"
assert result.review_status == "approved"
```

The returned `MerchantResult` includes the unchanged `description`, `merchant_name`, `review_status`, `method`, and `mapping_version`. Exact matches use method `exact_description`; unresolved results have no merchant and method `none`. `None`, blank, and unknown descriptions remain unresolved. Other description types raise `TypeError`; invalid table entries or blank versions raise `ValueError`.

Lookup preserves case and whitespace and does not clean the input. Pass Finance Foundry's cleaned `description` as supplied. Each table key has a single approved merchant value; unapproved suggestions must not be included. A dictionary cannot detect conflicting entries overwritten before it was passed to the function: any future table loader must reject conflicting approvals before constructing the dictionary. The caller supplies a version identifying the approved table snapshot; persistent version storage is not implemented. The function performs no writes and leaves its inputs unchanged.

Run the synthetic unit tests from the repository root:

```powershell
python -m unittest discover -s tests -v
```

The current function does not accept a transaction date or select effective-dated mappings. Its example above demonstrates the existing exact-lookup mechanism only; it does not yet implement the date-aware design below.

## What the application does

Merchant Normalization resolves each transaction description to the most recognizable business identity supported by evidence at the transaction date, using effective-dated mappings.

The application will use Finance Foundry's cleaned `description` as the stable key in a reusable merchant-mapping table. Multiple transactions with the same `description` within the same effective period will resolve through the same approved merchant mapping. The same description may resolve to a different business identity in a different period; amounts and source files do not change that lookup. Multiple descriptions may map to the same merchant. Transaction-description cleaning remains separate from identifying the underlying merchant. Approved mappings will use deterministic, explainable rules. Rules and approvals will be versioned so equal inputs under equal rules produce equal outputs.

Fuzzy, heuristic, or model-generated matches will remain suggestions until reviewed and approved. Unknown or ambiguous cases will remain unresolved rather than being assigned an invented merchant.

### Evidence and effective dates

A transaction descriptor may name a legal entity or local franchise operator while the customer recognizes a trading name or brand. Use the recognizable business identity only when evidence supports that relationship at the transaction date. A receipt, invoice, customer confirmation tied to the transaction, or dated business record can support review; retain references and the period supported. A present-day search result alone does not establish a historical relationship. Phone numbers or apparent name similarity alone do not establish an approved mapping.

Each mapping will record `effective_from` (inclusive) and `effective_to` (exclusive), with an absent end date representing open-ended validity. A transaction matches when its date is on or after the start and before the end, if present. Approved periods for the same description must not overlap. Missing or invalid transaction dates, uncovered periods, and insufficient evidence yield unresolved results; overlapping approvals are a validation error. Do not automatically extend evidence beyond the period it supports.

For example, a **synthetic** descriptor `EXAMPLE LOCAL SERVICES LLC` might map to `Example Home Care` during an evidenced franchise period and `Example Independent Services` during a later evidenced period. These are illustrative identities, not approved mappings. Historical transactions retain the identity applicable to their date instead of inheriting today's brand.

Effective dates describe business validity. Mapping versions and approval timestamps describe what was recorded or approved and when; retain both so a lookup can be reproduced using the same description, transaction date, and mapping snapshot.

## Input

The intended source is Finance Foundry's `trans_export` Athena view. The following columns and R display types were supplied from an exported sample. They document the observed export, not a verified Athena schema or access contract.

| Column | Observed R display type |
| --- | --- |
| `source_file_name` | `char` |
| `source_system` | `char` |
| `account_label` | `char` |
| `account_type` | `char` |
| `institution` | `char` |
| `transaction_dt` | `IDat` |
| `source_description` | `char` |
| `description` | `char` |
| `amount` | `num` |
| `check_number` | `char` |
| `status` | `char` |
| `transaction_type` | `char` |
| `transaction_subtype` | `char` |
| `matched_transaction_type_rule_id` | `char` |

### Synthetic sample rows

These invented rows illustrate the supplied export structure without publishing actual transactions or account details. All values are synthetic; the rule identifiers are illustrative and do not document Finance Foundry's real rules. In this example only, `null` represents a missing value and `""` represents an empty string; the actual export serialization must still be specified.

```json
[
  {
    "source_file_name": "demo_202501.csv",
    "source_system": "demo_card",
    "account_label": "Example Credit Card",
    "account_type": "credit_card",
    "institution": "Example Bank",
    "transaction_dt": "2025-01-10",
    "source_description": "EXAMPLE CAFE     EXAMPLE CITY     ZZ",
    "description": "EXAMPLE CAFE EXAMPLE CITY ZZ",
    "amount": -12.34,
    "check_number": null,
    "status": null,
    "transaction_type": "purchase",
    "transaction_subtype": "",
    "matched_transaction_type_rule_id": "DEMO_PURCHASE_001"
  },
  {
    "source_file_name": "demo_202501.csv",
    "source_system": "demo_card",
    "account_label": "Example Credit Card",
    "account_type": "credit_card",
    "institution": "Example Bank",
    "transaction_dt": "2025-01-11",
    "source_description": "EXAMPLE ONLINE PAYMENT",
    "description": "EXAMPLE ONLINE PAYMENT",
    "amount": 100.00,
    "check_number": null,
    "status": null,
    "transaction_type": "payment",
    "transaction_subtype": "",
    "matched_transaction_type_rule_id": "DEMO_PAYMENT_001"
  }
]
```

The supplied sample shows spacing differences between `source_description` and `description`. Neither field should be treated as an approved merchant identity. The existing `matched_transaction_type_rule_id` concerns transaction classification; it is not evidence of a merchant mapping or a stable transaction identifier. The meaning of amount signs must also be verified rather than inferred from these examples.

### Contract still to verify

`description` identifies a reusable merchant mapping, not an individual financial transaction. Repeated descriptions in transaction input are expected and must not be rejected as duplicate transaction keys. A unique transaction identifier is not required for this mapping table. The stability and equality semantics of the cleaned description still need to be verified.

Before implementing a live adapter, the input contract must establish:

- The `description` field's type, nullability, encoding, equality semantics, and stability under Finance Foundry's cleaning rules. Define how missing or blank descriptions are handled and how cleaning-rule changes affect existing mappings.
- The `transaction_dt` type, date interpretation, and missing/invalid-date policy needed to select an effective mapping.
- The original transaction description field or fields and their types, encoding, and handling of missing values.
- The source fields available for preservation and any additional context explicitly required by matching rules. Their names, types, and meanings must be verified rather than inferred.
- The view's row granularity, duplicate behavior, and treatment of corrected or updated transactions.
- The authorized AWS location and access configuration, to be verified before any live connection.

The application will validate the agreed schema and description keys. The approved mapping table must contain at most one applicable approved mapping per `description` and transaction date; overlapping approved periods and conflicting approvals must fail explicitly. Missing or blank descriptions must remain unresolved under an explicit policy. Repeated descriptions in transaction input are valid. Original descriptions, amounts, and all other source fields will be preserved exactly. Actual transactions, account information, credentials, and other private financial data must never be committed to this repository.

## Output

The application will produce a separate, reusable merchant-mapping table keyed by `description`. Transactions will look up their merchant using that cleaned description and select the approved period containing `transaction_dt`, so many transactions can reuse one mapping without requiring a unique transaction identifier. Applying the current approved mapping must preserve transaction row counts and source values; review suggestions or historical versions must not multiply transaction rows. It will never modify Finance Foundry source files, existing Athena views, raw records, or transaction exports.

The logical output contract requires the following information. These are conceptual requirements, not verified physical column names or a finalized storage schema.

| Information | Purpose |
| --- | --- |
| `description` | Reusable lookup key; transaction date selects its applicable mapping period. |
| Effective dates | Inclusive `effective_from` and exclusive `effective_to`; absent end means open-ended. |
| Evidence references | Support the business identity relationship and its applicable period. |
| Original description reference | Preserves provenance to the source description used to establish the mapping, separately from the lookup key. |
| Proposed or approved merchant | Records the most recognizable business identity supported by evidence for the applicable period. |
| Matching method | Explains how the result was obtained. |
| Rule identifier and version | Supports reproducibility and auditing of rule-based results. |
| Review status | Distinguishes suggestions requiring review, approved mappings, and unresolved cases. |

The lookup key is `description`, with at most one applicable approved mapping per transaction date. Multiple nonoverlapping historical periods may exist for each description. Types, remaining physical field names, merchant identity representation, allowed status values, storage format, and representation of review suggestions and version history remain to be specified. Suggestions must remain distinguishable from approved mappings, and unresolved cases must not imply an approved merchant.

## Operating principles and current scope

The intended implementation is a small Python package with a CLI, minimal dependencies, explicit configuration, and offline core matching logic. AWS access will be isolated in adapters. Dry-run will be the default; persistent writes will require an explicit apply flag. Production financial data access, AWS writes, and approval of merchant suggestions require authorization.

The supplied export structure is documented above, but the live Athena schema remains unverified. The current implementation is limited to offline exact lookup. Synthetic tests cover approved and unresolved results, similar descriptions remaining unresolved, exact-key selection, repeatability, input preservation, and invalid inputs. Transaction-date lookup, effective-dated mapping validation, evidence storage, a CLI, live adapter, table loader, and persistent approval/version history remain future work. Future date-aware tests must cover inclusive/exclusive boundaries, open-ended periods, gaps, overlapping approvals, missing dates, and historical identity changes.

Repository operating instructions are in [AGENTS.md](AGENTS.md).
