__author__ = "Chris Steel"
__copyright__ = "Copyright 2023, Syntheticore Corporation"
__credits__ = ["Chris Steel"]
__date__ = "2/9/2025"
__license__ = "Syntheticore Confidential"
__version__ = "1.0"
__email__ = "csteel@syntheticore.com"
__status__ = "Production"

import sys
import logging

from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI

from agentfoundry.utils.config import load_config
from agentfoundry.llm.ollama_llm import OllamaLLM


logger = logging.getLogger(__name__)


class LLMFactory:

    @staticmethod
    def get_llm_model(provider: str | None = None, llm_type: str | None = None):
        """
        Returns an instance of an LLM based on configuration.

        The configuration should define:
          - LLM_PROVIDER: e.g., "ollama" or "openai"
          - For Ollama:
              - OLLAMA.MODEL (default: "codegemma:7b-instruct")
              - OLLAMA.HOST (default: "http://127.0.0.1:11434")
          - For OpenAILLM:
              - OPENAI_API_KEY
              - OPENAI_MODEL (default: "gpt-3.5-turbo-0301")

        Raises:
            ValueError: If the LLM provider is unknown or the required settings are missing.
        """
        logger.info(f"Creating LLM")
        config = load_config()
        logger.info(f"Loaded configuration: {config.__dict__}")
        provider = provider or config.get("LLM_PROVIDER", "openai")  # Get the LLM provider from the config
        logger.info(f"Creating LLM model of type: {provider}")
        if provider == "ollama":
            model_name = config.get("OLLAMA.MODEL", "gemma3:27b")
            host = config.get("OLLAMA.HOST", "http://127.0.0.1:11434")
            logger.info(f"Using ChatOllama model: {model_name}")
            try:
                return OllamaLLM(model=model_name, base_url=host)
            except Exception as e:
                logger.error(f"Failed to create ChatOllama LLM: {e}")
                raise
        elif provider == "openai":
            openai_api_key = config.get("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY must be provided for OpenAILLM LLM.")
            # allow caller override via llm_type param
            model = llm_type or config.get("OPENAI_MODEL", "o4-mini")
            logger.info("Using OpenAI model: %s", model)
            try:
                llm = ChatOpenAI(model=model, api_key=openai_api_key)
                return llm
            except Exception as e:
                logger.error(f"Failed to create OpenAI LLM: {e}")
                raise
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")


# Quick test when running this module directly
if __name__ == "__main__":
    logger = logging.getLogger("simple_logger")
    logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all log levels

    # Create handler that outputs to stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)

    # Create a formatter and set it on the handler
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    stdout_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(stdout_handler)

    messages = [{"role": "user", "content": "Write a short poem about the stars."}]

    openai_llm = LLMFactory.get_llm_model(provider="openai")
    print("OpenAI LLM instance created:", openai_llm)
    output = openai_llm.invoke(messages)
    print("OpenAI Generated output:", output)

    ollama_llm = LLMFactory.get_llm_model(provider="ollama")
    print("Ollama LLM instance created:", ollama_llm)
    ollama_output = ollama_llm.invoke(messages)
    print("Ollama Generated output:", ollama_output.content)

