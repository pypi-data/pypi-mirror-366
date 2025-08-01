import importlib
import importlib.util
import logging
import os, sys
import traceback
from logging import getLogger
from typing import Dict, List, Optional, Union, Sequence

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import StructuredTool, Tool

from agentfoundry.llm.llm_factory import LLMFactory
from agentfoundry.utils.config import Config, load_config
from agentfoundry.utils.safe import safe_call


class ToolRegistry:
    """
    A registry to store and manage LangChain tools (agents) with unique command tags
    that the LLM can use.
    """

    def __init__(self):
        """
        Initializes the tool registry and logger.
        """
        self.config = load_config()
        self.logger = getLogger(self.__class__.__name__)
        self._tools: Dict[str, Tool] = {}

    def register_tool(self, tool: Tool | StructuredTool) -> None:
        """
        Registers a LangChain tool instance with validation.

        Args:
            tool (Tool): A LangChain Tool instance.
        """
        if not hasattr(tool, 'name'):
            tool.name = tool.__name__
            self.logger.error(f"Tool name set to default: {tool.__name__}")
        if (not hasattr(tool, 'description') or not isinstance(tool.description, str)
                or not tool.description or not tool.description.strip()):
            doc = tool.__doc__ if tool.__doc__ and tool.__doc__.strip() else "No description provided."
            tool.description = doc
            if not tool.__doc__ or not tool.__doc__.strip():
                tool.__doc__ = doc
            self.logger.warning(f"Tool '{tool.name}' has invalid or missing 'description' field. Using default description: {tool.description}")

        if tool.name in self._tools:
            self.logger.warning(f"Tool with name '{tool.name}' is already registered. Overriding.")

        self._tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")

    def get_tool(self, name: str) -> Optional[Tool]:
        """
        Retrieve a registered tool by its name.

        Args:
            name (str): The tool name.

        Returns:
            Tool or None: The registered tool if found, else None.
        """
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        """
        List the names of all registered tools.

        Returns:
            List[str]: A list of tool names.
        """
        return list(self._tools.keys())

    def inspect_tools(self, *args, **kwargs) -> str:
        """
        Generate a formatted string listing all available tools with descriptions.

        Args:
            *args: Variable positional arguments (ignored if passed).
            **kwargs: Variable keyword arguments (ignored if passed).

        Returns:
            str: A formatted summary of registered tools.
        """
        if args:
            self.logger.warning(f"Received unexpected positional arguments in inspect_tools: {args}")
        if kwargs:
            self.logger.warning(f"Received unexpected arguments in inspect_tools: {kwargs}")
        if not self._tools:
            return "No tools are currently registered."
        self.logger.info(f"Inspecting tools: {self._tools}")
        return "\n".join(f"{tool.name}: {tool.description}" for tool in self._tools.values())

    def as_langchain_tools(self) -> List[Tool]:
        """
        Returns all registered tools as a list of LangChain Tool instances.

        Returns:
            List[Tool]: A list of registered LangChain tools.
        """
        return list(self._tools.values())

    def load_tools_from_directory(
        self,
        directories: Optional[Union[str, Sequence[str]]] = None,
    ) -> None:
        """
        Load tools in several locations, in order:
          1) the built-in AgentFoundry shipped agents/tools directory;
          2) any application-provided static directories (one or more custom paths);
          3) (fallback) the configured TOOLS_DIR value from config.

        Args:
            directories (str or sequence of str, optional):
                One or more custom tool directories. If provided, these override
                the configured TOOLS_DIR; otherwise, looks for a TOOLS_DIRS list in config,
                then falls back to TOOLS_DIR.
        """
        config = Config()
        # 1) Load tools shipped with AgentFoundry itself
        shipped_tools_dir = os.path.join(
            os.path.dirname(__file__), '..', 'agents', 'tools'
        )
        self.logger.info(f"Loading shipped tools from: {shipped_tools_dir}")
        self._load_tools_from_single_directory(shipped_tools_dir, 'agentfoundry.agents.tools')

        # Determine custom static tool directories: explicit param or config TOOLS_DIRS
        custom_dirs = directories
        if custom_dirs is None:
            custom_dirs = config.get('TOOLS_DIRS', None)

        # Normalize to list
        if isinstance(custom_dirs, str):
            custom_dirs = [custom_dirs]

        # 2) Load from application-provided directories, if any
        if custom_dirs:
            for path in custom_dirs:
                self.logger.info(f"Loading tools from custom directory: {path}")
                self._load_tools_from_single_directory(path, None)
        else:
            # 3) Fallback to singular TOOLS_DIR
            tools_dir = config.get('TOOLS_DIR', None)
            self.logger.info(f"Loading tools from configured TOOLS_DIR: {tools_dir}")
            self._load_tools_from_single_directory(tools_dir, None)

    def _load_tools_from_single_directory(self, tools_dir: str, module_prefix: Optional[str]) -> None:
        """
        A function to load tools from a single directory into the registry.

        Args:
            tools_dir (str): Directory containing tool modules.
            module_prefix (str, optional): Module prefix for import (e.g., 'agentfoundry.agents.tools'). None for absolute paths.
        """
        if not tools_dir:
            self.logger.warning("Tools directory is not configured (None). Skipping loading custom tools.")
            return

        if not os.path.isdir(tools_dir):
            self.logger.warning(f"Tools directory does not exist or is not a directory: {tools_dir}")
            try:
                os.makedirs(tools_dir, exist_ok=True)
                self.logger.info(f"Created tools directory: {tools_dir}")
            except Exception as e:
                self.logger.warning(f"Could not create tools directory {tools_dir}: {e}")
            return

        self.logger.info(f"Loading tools from directory: {tools_dir}")

        import re
        for filename in os.listdir(tools_dir):
            if filename.startswith("__"):
                continue
            # Support Python source (.py) or compiled extension (.so, .pyd) modules
            if filename.endswith(".py"):
                tool_name = filename[:-3]
            # else:
                m = re.match(r"^(?P<name>.+?)(?:\..+)?\.(?:so|pyd|py)$", filename)  # including py for now
                if not m:
                    continue
                tool_name = m.group("name")
                if module_prefix:
                    full_module_name = f"{module_prefix}.{tool_name}"
                else:
                    # For DATA_DIR, use an absolute path
                    module_path = os.path.join(tools_dir, filename)
                    spec = importlib.util.spec_from_file_location(tool_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    full_module_name = tool_name

                self.logger.info(f"Loading tool from file: {filename}")
                module = safe_call(
                    lambda: importlib.import_module(full_module_name) if module_prefix else module,
                    self.logger,
                    f"Failed to load tool module {full_module_name}: {{e}}",
                    exc_info=True,
                )
                if not module:
                    continue
                self.logger.info(f"Loaded module: {full_module_name}")
                tools_found = False
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, (Tool, StructuredTool)):
                        if "name" not in attr.__dict__ or "description" not in attr.__dict__:
                            self.logger.warning(
                                f"Tool {attr_name} missing 'name' or 'description'; skipping"
                            )
                            continue
                        self.register_tool(attr)
                        tools_found = True
                if not tools_found:
                    self.logger.info(f"No valid Tool instances found in {full_module_name}")

    def as_langchain_registry_tool(self):
        """
        Returns the registry as a LangChain Tool instance for use in the LLM.

        Returns:
            Tool: A LangChain Tool instance representing the registry.
        """
        return Tool(name="tool_registry", func=self.inspect_tools, description="List all registered tools")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s - %(name)-32s:%(lineno)-5s  - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    stdout_handler.setFormatter(formatter)
    # Add the handler to the logger
    logging.getLogger().addHandler(stdout_handler)
    logging.getLogger("httpcore").setLevel(logging.WARNING)  # Suppress httpcore warnings
    logging.getLogger("openai").setLevel(logging.WARNING)  # Suppress OpenAI warnings
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logger = getLogger("agentfoundry.registry.tool_registry")

    registry = ToolRegistry()
    registry.load_tools_from_directory()
    tools = registry.list_tools()
    print(f"Loaded tools: {tools}")

    llm = LLMFactory.get_llm_model()
    template = """
    You have access to the following tools:

    {tools}

    Use the following format:

    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, could be one or more of [{tool_names}]
    Action Input: The required fields for the tool as specified by the tool.
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    Begin!

    Question: {input}
    Thought:{agent_scratchpad}
    """
    react_prompt = PromptTemplate(input_variables=["input", "agent_scratchpad"], template=template)
    agent = create_react_agent(llm, registry.as_langchain_tools(), react_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=registry.as_langchain_tools(), handle_parsing_errors=True)
    try:
        events = agent_executor.stream({
            "input": "Search for information about what AlphaSix Corp. does.",
            "tools": registry.inspect_tools(),
            "tool_names": ", ".join(registry.list_tools()),
            "agent_scratchpad": ""
        })

        for event in events:
            print(event['messages'][0].content)
            print('--' * 20)
    except Exception as ex:
        print(f"Error streaming agent: {ex}\n\n")
        traceback.print_exc()
