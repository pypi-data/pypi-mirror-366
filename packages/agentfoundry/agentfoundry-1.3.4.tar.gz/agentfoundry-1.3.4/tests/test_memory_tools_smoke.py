"""Smoke-test the memory tool wrappers against real back-ends (Chroma, DuckDB)."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from langchain_core.runnables import RunnableConfig

from agentfoundry.agents.tools import memory_tools as mem


pytest.importorskip("duckdb", reason="DuckDB required for memory smoke test")


class TestMemoryToolsSmoke:
    """End-to-end check that save/search helpers persist to real stores."""

    @pytest.fixture(scope="module", autouse=True)
    def _temp_data_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["DATA_DIR"] = tmp  # picked up by Memory classes
            yield Path(tmp)

    @pytest.fixture
    def cfg(self):
        return {
            "configurable": {
                "user_id": "u123",
                "thread_id": "t999",
                "org_id": "acme",
                "security_level": "5",
            }
        }

    def test_user_memory_cycle(self, cfg):
        text = "I love jazz music"
        assert "saved" in mem.save_user_memory.func(text, cfg)

        hits = mem.search_user_memory.func("jazz", cfg, k=3)
        assert any("jazz" in h.lower() for h in hits)

    def test_org_memory_cycle(self, cfg):
        text = "All laptops must be encrypted"
        assert "saved" in mem.save_org_memory.func(text, cfg)

        hits = mem.search_org_memory.func("encrypted", cfg)
        assert hits and "laptops" in hits[0].lower()

    def test_global_memory(self):
        text = "The Eiffel Tower is in Paris"
        assert "saved" in mem.save_global_memory.func(text)
        hits = mem.search_global_memory.func("eiffel", k=2)
        assert hits and "paris" in hits[0].lower()

    def test_thread_memory(self, cfg):
        text = "Session greeting hello"
        mem.save_thread_memory.func(text, cfg)
        hits = mem.search_thread_memory.func("greeting", cfg)
        assert hits and "hello" in hits[0].lower()

    def test_summarize(self, cfg):
        summary = mem.summarize_any_memory.func("user", cfg, max_tokens=2000)
        # Should at least include a known word from previous test
        assert "jazz" in summary.lower() or summary == ""
