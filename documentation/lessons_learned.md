# Merchant normalization lessons learned

## A transfer description can name a counterparty

When a description begins with `M. I. T FEDERAL CU TRANSFER`, resolve it to `MIT Federal CU`. The credit-union name identifies the counterparty. The word `TRANSFER` describes the transaction and adds no identity information. Ignore the reference number and personal name that follow it.

Apply this rule to transfer rows with the explicit credit-union prefix. A generic transfer without an identifiable counterparty remains unresolved. Preserve the original description and record the rule used to derive the merchant.

## A descriptor can name both a platform and a store

The ACH descriptor containing `DOORDASH SHEETZ ACH CONV CK` names DoorDash as the ordering platform and Sheetz as the store. Either identity can be useful, depending on how the customer reports spending. This may warrant a customer-specific mapping choice.

For this customer, resolve this descriptor to `DoorDash` so the downstream categorization step can map it to `Dining Out`. Preserve both names in the original description. Treat the choice as a customer preference for this descriptor.

## Decisions from the remaining export review

The local review pass records a decision on each description in the queue. Identity suggestions use the text in the export as evidence and await review. Preserve the source description and use the decision reason to identify which rule fired or what evidence is missing.

### Suggest the identity named in the descriptor

| Pattern | Decision | Transactions |
| --- | --- | ---: |
| Online bill pay with an explicit payee | Extract the name between `BILL PAY` and `ON-LINE`. Discard account references and dates. Keep the supplied name for providers such as PPL Electric Utilities and UGI Penn Natural Gas. | 874 |
| Named financial counterparty | Use the named issuer, lender, insurer, or service provider in a specific pattern such as `AMEX EPAYMENT ACH`, `FIDELITY FPRS`, or `SPRINT… ACHBILLPAY`. | 638 |
| Named storefront or service | Use a recognizable seller or service in a card or processor descriptor, such as Hulu, Duolingo, or Vrbo. A processor prefix alone supplies no seller identity. | 505 |
| Named deposit originator | Use the explicit organization in payroll or direct-deposit descriptions, such as Geisinger or GlaxoSmithKline. The merchant field represents the named counterparty in this export. | 372 |
| ACH conversion with an explicit name | Use The New York Times, IMSLP, Canva, or TikTok Shop when the matching name precedes `ACH CONV CK`. Discard the ACH suffix and account-holder text. | 41 |
| Named purchase return | Reuse the card descriptor rule when the return explicitly identifies the original merchant. | 13 |
| Converted check with an explicit payee | Use the named Passport Services or IRS payee in the conversion details. | 5 |

### Skip merchant normalization or flag missing source detail

| Pattern | Decision | Transactions |
| --- | --- | ---: |
| Numbered check without a payee | Set `insufficient_information` and keep normalization required. Route missing payee details to upstream remediation. | 220 |
| Missing or generic description | Set `insufficient_information` and keep normalization required. Examples include blank values, `NA`, and bare `WITHDRAWAL` or `DEPOSIT`. | 51 |
| Mobile deposit with a reference | Set `merchant_normalization_required = false`. The reference identifies the deposit event. | 67 |
| Overdraft funding from a credit card or line | Set `merchant_normalization_required = false`. The description identifies an account funding movement. | 62 |
| ATM cash deposit or in-branch electronic deposit | Set `merchant_normalization_required = false` for these explicit channel descriptions. Keep deposits with a named originator or an unknown channel subject to their own rules. | 3 |

### Keep unresolved and record the next evidence needed

| Pattern | Decision | Transactions |
| --- | --- | ---: |
| Transfer with an unverified destination | Use the transfer record or a confirmed account mapping. Transfer direction and memo text can describe purpose without establishing merchant identity. | 870 |
| Descriptor without a supported identity rule | Check a receipt, statement detail, or customer-confirmed alias. A readable fragment can be retained for review. | 552 |
| ACH or EDI with an unverified originator | Check the originator field or ACH detail. A personal name, reference, or conversion code alone is insufficient. | 311 |
| Processor with an unverified recipient | Use processor transaction detail or a customer choice. Examples include generic PayPal and truncated ActBlue recipient names. | 287 |
| App-store entry with an unverified seller | Use the app-store receipt to identify the seller or service. | 140 |
| Deposit with an unverified originator | Use the remittance or deposit record to identify the payer. | 54 |
| Bill-pay alias with an unclear payee | Confirm the saved biller alias. A label such as `CRV LOAN` describes the obligation. | 20 |
| Other payment with an unclear payee | Check payment details for the beneficiary or account relationship. | 19 |
| Same description with conflicting source context | Require supporting evidence before assigning a single identity across the rows. | 2 |

The 2,309 transactions with an existing cleaned descriptor remain available for review. Repeated cleaned text can prioritize a group, and a single extracted fragment can help locate supporting evidence. Approval still requires evidence for the merchant and applicable period.
