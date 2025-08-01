from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from agentfoundry.utils.config import Config

try:
    from serpapi import GoogleSearch
except ImportError:
    GoogleSearch = None  # type: ignore
from langchain.tools import StructuredTool

from agentfoundry.utils.logger import get_logger

logger = get_logger(__name__)


class GoogleSearchInput(BaseModel):
    """
    Input schema for the SerpAPI Google search tool.
    """
    query: str = Field(..., description="The search query to run on Google via SerpAPI.")
    num_results: int = Field(10, description="The number of results to retrieve (default 10).")
    api_key: Optional[str] = Field(
        None,
        description="SerpAPI API key; defaults to the SERPAPI_API_KEY environment variable.",
    )


def google_search(
    query: str,
    num_results: int = 10,
    api_key: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Perform a Google search using SerpAPI and return the organic search results.

    Args:
        query (str): The search query.
        num_results (int): Number of results to retrieve.
        api_key (Optional[str]): SerpAPI API key (overrides SERPAPI_API_KEY env var).

    Returns:
        List[Dict[str, Any]]: A list of organic result entries (may be empty).
    """
    if GoogleSearch is None:
        raise ImportError(
            "The 'serpapi' package is required for google_search_tool; install via 'pip install google-search-results'"
        )
    key = api_key or Config().get("SERPAPI_API_KEY")
    if not key:
        raise ValueError(
            "SERPAPI_API_KEY must be provided as an argument or environment variable"
        )
    params = {
        "engine": "google",
        "q": query,
        "num": num_results,
        "api_key": key,
    }
    logger.info(f"Performing Google search (SerpAPI): query={query}, num_results={num_results}")
    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("organic_results", [])


google_search_tool = StructuredTool.from_function(
    func=google_search,
    name="google_search_tool",
    description=google_search.__doc__,
    args_schema=GoogleSearchInput,
)


if __name__ == "__main__":
    # Quick smoke test
    sample = GoogleSearchInput(query="OpenAI GPT-4", num_results=3)
    print(google_search(query=sample.query, num_results=sample.num_results))