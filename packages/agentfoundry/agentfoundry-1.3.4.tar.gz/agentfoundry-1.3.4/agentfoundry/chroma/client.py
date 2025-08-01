"""Shim module – migrated to agentfoundry.vectorstores.providers.chroma_client."""

from importlib import import_module as _import_module

_real = _import_module("agentfoundry.vectorstores.providers.chroma_client")

# Re-export everything for backwards compatibility
globals().update(_real.__dict__)

