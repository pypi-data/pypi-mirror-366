"""LangChain tool wrappers around the new Memory classes.

These expose the classic `save_*_memory`, `search_*_memory` … names so that
existing prompts / agents continue to work while delegating to the modern
Memory layer (ThreadMemory, UserMemory, OrgMemory, GlobalMemory).
"""

from __future__ import annotations

from typing import Any, Dict, List

from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig
from typing_extensions import TypedDict

from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

# utilities
from agentfoundry.vectorstores.factory import VectorStoreFactory
from agentfoundry.utils.config import Config

# ---------------------------------------------------------------------------
# Runtime helpers
# ---------------------------------------------------------------------------


class _Cfg(TypedDict):
    configurable: Dict[str, str]


def _get(cfg: RunnableConfig, key: str) -> str | None:  # noqa: D401
    return cfg.get("configurable", {}).get(key) if cfg else None


def _provider_for_level(cfg: RunnableConfig | None, *, level: str):  # noqa: D401
    """Return a VectorStore provider for *level* using org_id when needed."""

    org_id = _get(cfg, "org_id") if level in ("thread", "user", "org") else None
    return VectorStoreFactory.get_provider(org_id=org_id)


# ---------------------------------------------------------------------------
# Thread-level tools
# ---------------------------------------------------------------------------


@tool
def save_thread_memory(text: str, config: RunnableConfig) -> str:  # noqa: D401
    """Save text in the current thread’s short-term memory."""
    from agentfoundry.agents.memory.thread_memory import ThreadMemory

    uid = _get(config, "user_id") or ""
    tid = _get(config, "thread_id") or "default"
    oid = _get(config, "org_id") or Config().get("ORG_ID", "")

    ThreadMemory(user_id=uid, thread_id=tid, org_id=oid).add(text)
    return "thread memory saved"


@tool
def search_thread_memory(query: str, config: RunnableConfig, k: int = 5) -> List[str]:
    """Search within the current thread’s memory (returns text snippets)."""
    from agentfoundry.agents.memory.thread_memory import ThreadMemory

    uid = _get(config, "user_id") or ""
    tid = _get(config, "thread_id") or "default"
    oid = _get(config, "org_id") or Config().get("ORG_ID", "")

    return ThreadMemory(user_id=uid, thread_id=tid, org_id=oid).similarity_search(query, k)


@tool
def delete_thread_memory(query: str, config: RunnableConfig, k: int = 5) -> str:  # noqa: D401
    """Delete up to *k* matching snippets from the current thread memory."""
    from agentfoundry.agents.memory.thread_memory import ThreadMemory

    uid = _get(config, "user_id") or ""
    tid = _get(config, "thread_id") or "default"
    oid = _get(config, "org_id") or Config().get("ORG_ID", "")

    mem = ThreadMemory(user_id=uid, thread_id=tid, org_id=oid)
    docs = mem._index.similarity_search(query, k=k, filter={"user_id": uid, "thread_id": tid})  # type: ignore[attr-defined]  # pylint: disable=protected-access
    ids = [d.metadata.get("id", "") or d.id for d in docs]
    if ids:
        mem._index.delete(ids)
        mem._persist_index()
    return f"deleted {len(ids)} docs"


# ---------------------------------------------------------------------------
# User-level tools
# ---------------------------------------------------------------------------


@tool
def save_user_memory(text: str, config: RunnableConfig) -> str:  # noqa: D401
    """Save *text* into the caller’s user-level long-term memory."""
    from agentfoundry.agents.memory.user_memory import UserMemory

    uid = _get(config, "user_id")
    oid = _get(config, "org_id") or Config().get("ORG_ID", "")
    caller_level = int(_get(config, "role_level") or 0)
    if not uid:
        return "user_id missing in config"
    UserMemory(uid, org_id=oid).add_semantic_item(text)
    return "user memory saved"


@tool
def search_user_memory(query: str, config: RunnableConfig, k: int = 10) -> List[str]:
    """Search user memory and global memory, returning up to *k* snippets."""
    from agentfoundry.agents.memory.user_memory import UserMemory
    from agentfoundry.agents.memory.global_memory import GlobalMemory

    uid = _get(config, "user_id")
    oid = _get(config, "org_id") or Config().get("ORG_ID", "")
    # Determine caller's role level if provided in the runnable configuration so that
    # the underlying memory implementation can enforce visibility restrictions.
    caller_level = int(_get(config, "role_level") or 0)
    if not uid:
        return []

    local = UserMemory(uid, org_id=oid).semantic_search(query, caller_role_level=caller_level, k=k)
    global_hits = GlobalMemory().search(query, k)
    return (local + global_hits)[:k]


@tool
def delete_user_memory(query: str, config: RunnableConfig, k: int = 5) -> str:  # noqa: D401
    """Delete up to *k* user-level memory snippets matching *query*."""
    from agentfoundry.agents.memory.user_memory import UserMemory

    uid = _get(config, "user_id")
    oid = _get(config, "org_id") or Config().get("ORG_ID", "")
    if not uid:
        return "user_id missing"

    mem = UserMemory(uid, org_id=oid)
    docs = mem._vs_provider.similarity_search(query, k=k, where={"user_id": uid})  # type: ignore[attr-defined]  # pylint: disable=protected-access
    mem._vs_provider.delete(ids=[d.metadata.get("id", "") or d.id for d in docs])  # type: ignore[attr-defined]
    return f"deleted {len(docs)} docs"


# ---------------------------------------------------------------------------
# Organisation-level tools
# ---------------------------------------------------------------------------


@tool
def save_org_memory(text: str, config: RunnableConfig) -> str:  # noqa: D401
    """Persist *text* in the organisation’s shared long-term memory."""
    from agentfoundry.agents.memory.org_memory import OrgMemory

    oid = _get(config, "org_id")
    if not oid:
        return "org_id missing in config"
    OrgMemory(oid).add_semantic_item(text)
    return "org memory saved"


@tool
def search_org_memory(query: str, config: RunnableConfig, k: int = 8) -> List[str]:
    """Search organisation + global memories for *query*.

    Returns up to *k* snippets sorted by relevance."""
    from agentfoundry.agents.memory.org_memory import OrgMemory
    from agentfoundry.agents.memory.global_memory import GlobalMemory

    oid = _get(config, "org_id")
    if not oid:
        return []
    org_hits = OrgMemory(oid).semantic_search(query, k)
    global_hits = GlobalMemory().search(query, k)
    return (org_hits + global_hits)[:k]


@tool
def delete_org_memory(query: str, config: RunnableConfig, k: int = 5) -> str:  # noqa: D401
    """Delete up to *k* organisation-level memory snippets."""
    from agentfoundry.agents.memory.org_memory import OrgMemory

    oid = _get(config, "org_id")
    if not oid:
        return "org_id missing"
    mem = OrgMemory(oid)
    docs = mem._vs_provider.similarity_search(query, k=k)  # type: ignore[attr-defined]  # pylint: disable=protected-access
    mem._vs_provider.delete(ids=[d.metadata.get("id", "") or d.id for d in docs])  # type: ignore[attr-defined]
    return f"deleted {len(docs)} docs"


# ---------------------------------------------------------------------------
# Global-level tools
# ---------------------------------------------------------------------------


@tool
def save_global_memory(text: str) -> str:  # noqa: D401
    """Add *text* to the system-wide global memory store."""
    from agentfoundry.agents.memory.global_memory import GlobalMemory

    GlobalMemory().add_document(text)
    return "global memory saved"


@tool
def search_global_memory(query: str, k: int = 5) -> List[str]:
    """Search global memory for *query* (up to *k* results)."""
    from agentfoundry.agents.memory.global_memory import GlobalMemory

    return GlobalMemory().search(query, k)


@tool
def delete_global_memory(query: str, k: int = 5) -> str:  # noqa: D401
    """Delete up to *k* global memory snippets matching *query*."""
    from agentfoundry.agents.memory.global_memory import GlobalMemory

    mem = GlobalMemory()
    docs = mem._vs_provider.similarity_search(query, k=k)  # type: ignore[attr-defined]  # pylint: disable=protected-access
    mem._vs_provider.delete(ids=[d.metadata.get("id", "") or d.id for d in docs])  # type: ignore[attr-defined]
    return f"deleted {len(docs)} docs"


# ---------------------------------------------------------------------------
# Summary helper (unchanged)
# ---------------------------------------------------------------------------


from agentfoundry.agents.memory.summary_utils import summarize_memory


@tool
def summarize_any_memory(level: str, config: RunnableConfig, max_tokens: int = 32_000) -> str:  # noqa: D401
    """Return a summarised view of the requested memory *level*.

    level can be one of ``thread``, ``user``, ``org`` or ``global``.
    The helper merges org/global data when appropriate and truncates to
    *max_tokens* tokens.
    """

    level = level.lower()
    filt: Dict[str, str] = {}
    if level == "user":
        filt["user_id"] = _get(config, "user_id") or ""  # type: ignore[arg-type]
    elif level == "org":
        filt["org_id"] = _get(config, "org_id") or ""  # type: ignore[arg-type]
    elif level == "thread":
        filt["thread_id"] = _get(config, "thread_id") or ""  # type: ignore[arg-type]

    return summarize_memory(filt, max_tokens=max_tokens)
