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
