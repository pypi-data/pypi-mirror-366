from langchain_core.tools import BaseTool
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun
from typing import Any

from saptiva_agents import DEFAULT_LANG, CONTENT_CHARS_MAX


class WikipediaSearch(BaseTool):
    """
    Tool for searching information on Wikipedia.

    Make sure to install Wikipedia:
        pip install wikipedia
    """
    def __init__(self):
        name = "WikipediaSearch"
        description = "Busca información en Wikipedia sobre un tema específico."
        super().__init__(name=name, description=description)

    def _run(self, query: str) -> Any:
        """
        Executes the Wikipedia query synchronously and returns the result.
        """
        api_wrapper = WikipediaAPIWrapper(
            doc_content_chars_max=CONTENT_CHARS_MAX,
            lang=DEFAULT_LANG,
            wiki_client="wikipedia"
        )
        tool = WikipediaQueryRun(api_wrapper=api_wrapper)

        result = tool.invoke({"query": query})
        return result

    async def _arun(self, query: str) -> Any:
        """
        Executes the Wikipedia query asynchronously and returns the result.
        """
        api_wrapper = WikipediaAPIWrapper(
            doc_content_chars_max=CONTENT_CHARS_MAX,
            lang=DEFAULT_LANG,
            wiki_client="wikipedia"
        )
        tool = WikipediaQueryRun(api_wrapper=api_wrapper)
        result = tool.invoke({"query": query})

        return result
