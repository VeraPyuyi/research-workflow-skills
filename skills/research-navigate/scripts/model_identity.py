"""Explicit reviewed native IDs and conservative cross-version family identity."""
LEGACY_NATIVE_MODELS = frozenset(("gpt-6-astra", "gpt-6.1-sol", "gpt-6-luna"))
NATIVE_MODELS = LEGACY_NATIVE_MODELS | {"gpt-6.2-astra", "gpt-6.2-sol"}
FAMILIES = {
    "gpt-6-astra": "gpt-astra",
    "gpt-6.2-astra": "gpt-astra",
    "gpt-6-sol": "gpt-sol",
    "gpt-6.1-sol": "gpt-sol",
    "gpt-6.2-sol": "gpt-sol",
    "gpt-6-luna": "gpt-luna",
}


def model_family(model, declared=None):
    suffix = model.split("/", 1)[-1].removesuffix("-free")
    return FAMILIES.get(suffix, declared or suffix)


def model_lineage(row):
    """Provider/base-model lineage from the registry; None when undocumented.

    Versions, channels, efforts and same-vendor product names share one lineage,
    so two GPT products or two Grok versions are not independent reviewers.
    """
    if not isinstance(row, dict) or row.get("kind", "generative") != "generative":
        return None
    lineage = row.get("lineage")
    return lineage if isinstance(lineage, str) and lineage.strip() else None
