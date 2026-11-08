# Merchant Normalization

Merchant Normalization is an independent, downstream component of Finance Foundry. Finance Foundry ingests and harmonizes transactions from multiple sources; Merchant Normalization is intended to identify the merchants represented in those transactions and produce a separate, auditable merchant-mapping overlay.

This repository currently contains project documentation only. The behavior and contracts below describe the intended application; no normalization code or live AWS adapter has been implemented.

## What the application does

The application will keep transaction-description cleaning separate from identifying the underlying merchant. Approved mappings will use deterministic, explainable rules. Rules and approvals will be versioned so equal inputs under equal rules produce equal outputs.

Fuzzy, heuristic, or model-generated matches will remain suggestions until reviewed and approved. Unknown or ambiguous cases will remain unresolved rather than being assigned an invented merchant.

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

No explicit transaction identifier appears among the supplied columns. Neither a row number nor a combination of filename, date, description, and amount can be assumed unique or stable: distinct transactions may share those values. A stable identifier remains a prerequisite for linking the output overlay safely.

Before implementing a live adapter, the input contract must establish:

- A stable transaction identifier, including its type, scope, uniqueness, nullability, and stability across repeated exports or source updates. If a composite key is required, its components and guarantees must be verified.
- The original transaction description field or fields and their types, encoding, and handling of missing values.
- The source fields available for preservation and any additional context explicitly required by matching rules. Their names, types, and meanings must be verified rather than inferred.
- The view's row granularity, duplicate behavior, and treatment of corrected or updated transactions.
- The authorized AWS location and access configuration, to be verified before any live connection.

The application will validate the agreed schema and key uniqueness and fail explicitly on missing or inconsistent identifiers. Original descriptions, amounts, and all other source fields will be preserved exactly. Actual transactions, account information, credentials, and other private financial data must never be committed to this repository.

## Output

The application will produce a separate merchant-mapping overlay that can be associated with the source transactions through the verified stable transaction identifier. It will never modify Finance Foundry source files, existing Athena views, raw records, or transaction exports.

The logical output contract requires the following information. These are conceptual requirements, not verified physical column names or a finalized storage schema.

| Information | Purpose |
| --- | --- |
| Verified transaction identifier | Associates each result with its original transaction. |
| Original description reference | Traces the result back to the exact source description. |
| Proposed or approved merchant | Records the merchant suggestion or approved identity, when one exists. |
| Matching method | Explains how the result was obtained. |
| Rule identifier and version | Supports reproducibility and auditing of rule-based results. |
| Review status | Distinguishes suggestions requiring review, approved mappings, and unresolved cases. |

The physical field names, types, merchant identity representation, allowed status values, output cardinality, and storage format remain to be specified. Suggestions must remain distinguishable from approved mappings, and unresolved cases must not imply an approved merchant.

## Operating principles and current scope

The intended implementation is a small Python package with a CLI, minimal dependencies, explicit configuration, and offline core matching logic. AWS access will be isolated in adapters. Dry-run will be the default; persistent writes will require an explicit apply flag. Production financial data access, AWS writes, and approval of merchant suggestions require authorization.

The first milestone is to document and verify the required input contract and define the output overlay schema. The supplied export structure is documented above, but the live Athena schema remains unverified. No AWS connection is made and no application code is implemented as part of this documentation milestone. Future automated tests will use synthetic fixtures and cover ambiguity, rule precedence, idempotence, and preservation of original records.

Repository operating instructions are in [AGENTS.md](AGENTS.md).
