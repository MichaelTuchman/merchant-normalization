# Merchant normalization lessons learned

## A transfer description can name a counterparty

When a description begins with `M. I. T FEDERAL CU TRANSFER`, resolve it to `MIT Federal CU`. The credit-union name identifies the counterparty. The word `TRANSFER` describes the transaction and adds no identity information. Ignore the reference number and personal name that follow it.

Apply this rule to transfer rows with the explicit credit-union prefix. A generic transfer without an identifiable counterparty remains unresolved. Preserve the original description and record the rule used to derive the merchant.

## A descriptor can name both a platform and a store

The ACH descriptor containing `DOORDASH SHEETZ ACH CONV CK` names DoorDash as the ordering platform and Sheetz as the store. Either identity can be useful, depending on how the customer reports spending. This may warrant a customer-specific mapping choice.

For this customer, resolve this descriptor to `DoorDash` so the downstream categorization step can map it to `Dining Out`. Preserve both names in the original description. Treat the choice as a customer preference for this descriptor.
