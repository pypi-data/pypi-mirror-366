import pytest

import agentfoundry.agents.orchestrator as orchestrator_module
from agentfoundry.agents.orchestrator import Orchestrator


class DummyRegistryNoAttr:
    """Registry stub without agent_tools attribute."""
    pass


class DummyRegistryWithInvalidAttr:
    """Registry stub with agent_tools attribute of wrong type."""
    agent_tools = ["not", "a", "dict"]


class DummyRegistryValid:
    """Registry stub with valid agent_tools mapping."""
    def __init__(self):
        self.agent_tools = {"agentA": []}


class DummySupervisorBuilder:
    """Stub for create_supervisor return value, with compile()."""
    def __init__(self, *args, **kwargs):
        pass

    def compile(self, checkpointer):
        return "compiled_supervisor"


@pytest.fixture(autouse=True)
def stub_orchestrator_dependencies(monkeypatch):
    """
    Stub out heavy dependencies for Orchestrator.__init__, so tests focus on agent_tools validation.
    """
    # Stub LLMFactory.get_llm_model to avoid external LLM initialization
    class DummyLLMFactory:
        @staticmethod
        def get_llm_model():
            return "dummy_llm"

    monkeypatch.setattr(orchestrator_module, "LLMFactory", DummyLLMFactory)
    # Stub make_specialist to avoid building real agents
    monkeypatch.setattr(orchestrator_module, "make_specialist", lambda name, tools, llm, prompt=None: f"specialist_{name}")
    # Stub create_supervisor to return builder with compile()
    monkeypatch.setattr(orchestrator_module, "create_supervisor", lambda **kwargs: DummySupervisorBuilder())
    # Stub fallback _create_react_agent
    monkeypatch.setattr(orchestrator_module, "_create_react_agent", lambda **kwargs: "fallback_supervisor")
    # Stub MemorySaver
    monkeypatch.setattr(orchestrator_module, "MemorySaver", lambda *args, **kwargs: None)
    yield


def test_missing_agent_tools_raises():
    """Initializing with no agent_tools should raise a RuntimeError."""
    with pytest.raises(RuntimeError) as excinfo:
        Orchestrator(DummyRegistryNoAttr())
    assert "Tool registry 'agent_tools' mapping missing or invalid" in str(excinfo.value)


def test_agent_tools_not_dict_raises():
    """Initializing with agent_tools not being a dict should raise a RuntimeError."""
    with pytest.raises(RuntimeError) as excinfo:
        Orchestrator(DummyRegistryWithInvalidAttr())
    assert "Tool registry 'agent_tools' mapping missing or invalid" in str(excinfo.value)


def test_valid_agent_tools_initializes():
    """With a valid agent_tools dict, Orchestrator should initialize and set attributes."""
    dummy_registry = DummyRegistryValid()
    orch = Orchestrator(dummy_registry, llm="provided_llm")
    # Registry should be stored
    assert orch.registry is dummy_registry
    # Counter initialized to zero
    assert orch.curr_counter == 0
    # Supervisor should be our stub compiled return value
    assert orch.supervisor == "compiled_supervisor"