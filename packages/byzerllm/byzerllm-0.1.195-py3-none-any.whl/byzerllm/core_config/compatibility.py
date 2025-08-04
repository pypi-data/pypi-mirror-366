"""
Compatibility functions for backward compatibility.

This module provides functions that maintain compatibility with
existing code that uses the old memory management interface.
"""

import threading
from typing import Dict, Any, Optional
from .main_manager import get_memory_manager


# Global instance cache for compatibility
_default_memory_manager: Optional['MemoryManager'] = None
_default_memory_manager_lock = threading.Lock()


def save_memory():
    """Save memory (compatibility function)."""
    global _default_memory_manager
    with _default_memory_manager_lock:
        if _default_memory_manager is None:
            _default_memory_manager = get_memory_manager()
    _default_memory_manager.save_memory()


def save_memory_with_new_memory(new_memory: Dict[str, Any]):
    """Save new memory (compatibility function)."""
    global _default_memory_manager
    with _default_memory_manager_lock:
        if _default_memory_manager is None:
            _default_memory_manager = get_memory_manager()
    _default_memory_manager.save_memory_with_new_memory(new_memory)


def load_memory() -> Dict[str, Any]:
    """Load memory (compatibility function)."""
    global _default_memory_manager
    with _default_memory_manager_lock:
        if _default_memory_manager is None:
            _default_memory_manager = get_memory_manager()
    return _default_memory_manager.get_memory_dict()


def get_memory() -> Dict[str, Any]:
    """Get memory (compatibility function)."""
    return load_memory()
