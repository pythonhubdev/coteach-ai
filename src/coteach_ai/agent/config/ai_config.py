from langchain_community.tools import TavilySearchResults
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

from src.coteach_ai.core import settings
from src.coteach_ai.errors import InvalidSearchToolError, UnKnownModelError


class AgentConfig:
	def __init__(self) -> None:
		self.llm: ChatOpenAI | None = None
		self.search_tool: TavilySearchResults | Tool | None = None
		self.initialize()

	def initialize(self):
		if settings.agent.MODEL == "OpenAI":
			self.llm = ChatOpenAI(
				organization=settings.agent.OPENAI_ORGANIZATION_ID,
				model=settings.agent.OPENAI_MODEL,
				max_retries=settings.agent.MAX_RETRIES,
			)
		else:
			raise UnKnownModelError(
				message="Model not supported at this moment. Please try with supported model.",
				status=500,
			)

		if settings.agent.SEARCH_TOOL == "tavily":
			self.search_tool = TavilySearchResults(
				max_results=20,
				include_answer=True,
			)
		elif settings.agent.SEARCH_TOOL == "google":
			search = GoogleSearchAPIWrapper()
			self.search_tool = Tool(
				name="google_search",
				description="Search Google for recent results.",
				func=search.run,
			)
		else:
			msg = "Invalid SEARCH_TOOL specified in settings.agent.SEARCH_TOOL"
			raise InvalidSearchToolError(
				message=msg,
				status=500,
			)


agent_config = AgentConfig()
