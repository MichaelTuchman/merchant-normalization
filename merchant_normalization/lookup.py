"""Exact lookup; description cleaning and mapping approval happen upstream."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class MerchantResult:
    """Lookup outcome with the unchanged input and mapping provenance."""

    description: str | None
    merchant_name: str | None
    review_status: Literal["approved", "unresolved"]
    method: Literal["exact_description", "none"]
    mapping_version: str


def normalize_merchant(
    description: str | None,
    approved_mappings: Mapping[str, str],
    *,
    mapping_version: str,
) -> MerchantResult:
    """Resolve an exact cleaned description using a caller-approved table.

    The table maps each description to one approved canonical merchant name.
    It must exclude suggestions and conflicting approvals before construction;
    a dict cannot detect duplicate keys already overwritten by its caller.
    Supply a version identifying the table snapshot for reproducibility.

    None, blank, and unknown descriptions are unresolved. Other input types
    and invalid table entries raise explicitly. No case folding, trimming,
    fuzzy matching, or persistent writes occur.
    """
    if description is not None and not isinstance(description, str):
        raise TypeError("description must be a string or None")
    if not isinstance(mapping_version, str) or not mapping_version.strip():
        raise ValueError("mapping_version must be a nonblank string")
    if not isinstance(approved_mappings, Mapping):
        raise TypeError("approved_mappings must be a mapping")
    for key, merchant in approved_mappings.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("mapping descriptions must be nonblank strings")
        if not isinstance(merchant, str) or not merchant.strip():
            raise ValueError("approved merchant names must be nonblank strings")

    merchant = (
        approved_mappings.get(description)
        if description is not None and description.strip()
        else None
    )
    return MerchantResult(
        description=description,
        merchant_name=merchant,
        review_status="approved" if merchant is not None else "unresolved",
        method="exact_description" if merchant is not None else "none",
        mapping_version=mapping_version,
    )
