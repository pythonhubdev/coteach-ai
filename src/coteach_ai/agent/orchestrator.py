from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command

from src.coteach_ai.core import settings

from ..errors import DataError
from .agent import State
from .filter_agent import filter_agent
from .organizer_agent import organizer_agent
from .research_agent import research_agent
from .visual_agent import visual_agent


class Orchestrator:
	def __init__(self) -> None:
		self.graph: CompiledStateGraph = self._build_graph()

	@staticmethod
	def _build_graph() -> CompiledStateGraph:  # noqa: C901
		builder = StateGraph(State)

		async def research_node(state: State) -> Command:
			update = await research_agent.run(state)
			return Command(update=update, goto="filter")

		async def filter_node(state: State) -> Command:
			update = await filter_agent.run(state)
			return Command(update=update, goto="organizer")

		async def organizer_node(state: State) -> Command:
			update = await organizer_agent.run(state)
			return Command(update=update, goto="visual")

		async def visual_node(state: State) -> Command:
			update = await visual_agent.run(state)
			return Command(update=update, goto="combine")

		async def combine_node(state: State) -> Command:  # noqa: C901
			if not state["organized_content"] or not state["visual_content"]:
				msg = "State must contain 'organized_content' and 'visual_content' to combine"
				raise DataError(message=msg, status=422)

			organized_content = state["organized_content"]
			visual_content = state["visual_content"]

			modules: list[dict[str, Any]] = []
			current_module: dict[str, Any] = {}
			for line in organized_content.split("\n"):
				_line = line.strip()
				if _line.startswith("### Module"):
					if current_module:
						modules.append(current_module)
					current_module = {"title": _line.replace("### ", "")}
				elif _line.startswith("- **Learning Objective**:"):
					current_module["learning_objective"] = _line.replace("- **Learning Objective**: ", "")
				elif _line.startswith("- **Content**:"):
					current_module["content"] = _line.replace("- **Content**: ", "")
				elif _line.startswith("- **Summary**:"):
					current_module["summary"] = _line.replace("- **Summary**: ", "")
				elif _line.startswith("- **Suggested Visuals**:"):
					current_module["suggested_visuals"] = _line.replace("- **Suggested Visuals**: ", "")
				elif _line and "content" in current_module:
					current_module["content"] += " " + _line
			if current_module:
				modules.append(current_module)

			visuals = {}
			current_title = None
			for _line in visual_content.split("\n"):
				_line = _line.strip()
				if _line.startswith("### Module"):
					current_title = _line.replace("### ", "")
					visuals[current_title] = {"image": "", "video": ""}
				elif _line.startswith("- **Image**:"):
					if current_title:
						visuals[current_title]["image"] = _line.replace("- **Image**: ", "")
				elif _line.startswith("- **Video**:"):
					if current_title:
						visuals[current_title]["video"] = _line.replace("- **Video**: ", "")

			combined_output: dict[str, dict[str, str | list | Any]] = {
				"course": {
					"title": state["initial_input"][0].content,
					"modules": [],
				},
			}
			for module in modules:
				title = module["title"]
				module_dict = {
					"title": title,
					"learning_objective": module.get("learning_objective", ""),
					"content": module.get("content", ""),
					"summary": module.get("summary", ""),
					"visuals": {
						"image": visuals.get(title, {}).get("image", ""),
						"video": visuals.get(title, {}).get("video", ""),
					},
				}
				assert combined_output["course"]["modules"] is not None
				assert isinstance(combined_output["course"]["modules"], list)
				combined_output["course"]["modules"].append(module_dict)

			return Command(update={"final_course": combined_output}, goto=END)

		builder.add_node("researcher", research_node)
		builder.add_node("filter", filter_node)
		builder.add_node("organizer", organizer_node)
		builder.add_node("visual", visual_node)
		builder.add_node("combine", combine_node)
		builder.add_edge(START, "researcher")
		builder.add_edge("researcher", "filter")
		builder.add_edge("filter", "organizer")
		builder.add_edge("organizer", "visual")
		builder.add_edge("visual", "combine")
		builder.add_edge("combine", END)

		return builder.compile(debug=settings.app.DEBUG)

	async def run(self, course_description: str) -> dict[str, Any]:
		"""Run the orchestrator to generate a course from a description."""
		initial_state: State = {
			"initial_input": [HumanMessage(content=course_description)],
			"research_summary": None,
			"filtered_modules": None,
			"organized_content": None,
			"visual_content": None,
			"final_course": None,
		}
		result = await self.graph.ainvoke(initial_state)
		return result["final_course"]


orchestrator = Orchestrator()
