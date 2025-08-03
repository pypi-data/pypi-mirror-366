# docore_ai/prompt_loader.py

import logging

logger = logging.getLogger(__name__)

class PromptLoaderError(Exception):
    """Raised when the prompt bundle cannot be loaded or parsed."""
    pass

# Module-level cache for the currently active prompt bundle
_CURRENT_BUNDLE = None

def load_local_bundle() -> dict:
    """
    Deprecated. Disk-based loading is disabled.
    """
    raise PromptLoaderError("Disk-based prompt loading is disabled.")

def set_current_bundle(bundle: dict):
    """
    Store the active prompt bundle in memory.
    """
    global _CURRENT_BUNDLE
    #dprint("✅ Prompt bundle has been set into memory.")
    _CURRENT_BUNDLE = bundle

def get_current_bundle() -> dict:
    """
    Return the in-memory prompt bundle, or raise if not initialized.
    """
    if _CURRENT_BUNDLE is None:
        raise PromptLoaderError("No prompt bundle available in memory.")
    return _CURRENT_BUNDLE
