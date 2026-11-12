# Merchant normalization lessons learned

## A transfer description can name a counterparty

When a description begins with `M. I. T FEDERAL CU TRANSFER`, resolve it to `MIT Federal CU`. The credit-union name identifies the counterparty. The word `TRANSFER` describes the transaction and adds no identity information. Ignore the reference number and personal name that follow it.

Apply this rule to transfer rows with the explicit credit-union prefix. A generic transfer without an identifiable counterparty remains unresolved. Preserve the original description and record the rule used to derive the merchant.
