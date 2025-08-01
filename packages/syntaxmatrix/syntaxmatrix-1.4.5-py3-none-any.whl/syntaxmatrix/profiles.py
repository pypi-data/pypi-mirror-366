# syntaxmatrix/profiles.py

from syntaxmatrix.llm_store import list_profiles, load_profile

# Preload once at import-time
_profiles: dict[str, dict] = {}
for entry in list_profiles():
    prof = load_profile(entry["name"])
    if prof:
        _profiles[entry["purpose"]] = prof

def get_profile(purpose: str) -> dict:
    """
    Return the full profile dict for that purpose (e.g. "chat", "embedding").
    Returns None if no such profile exists.
    """
    prof = _profiles.get(purpose, None)
    return prof
