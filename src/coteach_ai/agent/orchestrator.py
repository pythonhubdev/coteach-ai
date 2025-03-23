from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command
from loguru import logger

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

		def combine_node(state: State) -> Command:  # noqa: C901
			logger.info(f"The current state is {state}")
			if not state.get("organized_content") or not state.get("visual_content"):
				raise DataError(
					message="State must contain 'organized_content' and 'visual_content' to combine",
					status=422,
				)

			organized_content: str = state.get("organized_content", None) or ""
			visual_content: str = state.get("visual_content", None) or ""
			research_summary: str = state.get("research_summary", None) or ""
			input_content: str | list[str | dict[str, Any]] = state["initial_input"][0].content
			assert isinstance(input_content, str)
			if input_content.count("-") != 1:
				raise DataError(
					message="Input content must contain exactly one hyphen to separate brief and target audience",
					status=422,
				)
			unprocessed_brief, unprocessed_target_audience = input_content.split("-")
			brief = unprocessed_brief.replace("Brief: ", "").strip()
			target_audience = unprocessed_target_audience.replace("Target Audience: ", "").strip()

			topic = brief.split(" course")[0].replace("A ", "").capitalize()

			modules = []
			current_module = None
			current_lesson = None

			for line in organized_content.split("\n"):
				leading_tabs = 0
				while leading_tabs < len(line) and line[leading_tabs] == "\t":
					leading_tabs += 1
				remaining_line = line[leading_tabs:].lstrip()

				if leading_tabs == 0 and remaining_line.startswith("- ### "):
					if current_module:
						modules.append(current_module)
					current_module = {"title": remaining_line[len("- ### ") :].strip(), "lessons": []}
					current_lesson = None
				elif leading_tabs == 1 and remaining_line.startswith("- #### "):
					if current_module is None:
						continue
					if current_lesson:
						current_module["lessons"].append(current_lesson)
					current_lesson = {"title": remaining_line[len("- #### ") :].strip(), "content": "", "resources": []}
				elif leading_tabs == 2 and remaining_line.startswith("- **Content**: "):
					if current_lesson is not None:
						current_lesson["content"] = remaining_line[len("- **Content**: ") :].strip()
				elif leading_tabs == 2 and remaining_line.startswith("- **Resources**: "):
					if current_lesson is not None:
						resources = remaining_line[len("- **Resources**: ") :].strip().split(", ")
						current_lesson["resources"] = resources
				elif current_lesson and leading_tabs >= 2 and remaining_line:
					current_lesson["content"] += " " + remaining_line.strip()

			if current_lesson and current_module:
				current_module["lessons"].append(current_lesson)
			if current_module and current_module not in modules:
				modules.append(current_module)

			visuals = {}
			current_title = None
			for line in visual_content.split("\n"):
				_line = line.strip().strip("\n").strip("\t")
				if _line.startswith("- **Lesson"):
					current_title = _line.replace("-", "").strip(" ").strip("*")
					visuals[current_title] = []
				elif _line.startswith("- ") and "Lesson" not in _line and current_title:
					visuals[current_title].append(_line.replace("- ", ""))

			references = []
			in_references_section = False
			for line in research_summary.split("\n"):
				_line = line.strip()
				if _line.startswith(
					(
						"### References",
						"**References**",
						"References:",
						"### References:",
						"**References**:",
						"**References:**",
					),
				):
					in_references_section = True
					continue
				if in_references_section and _line.startswith("- "):
					ref = _line.replace("- ", "").strip()
					sentence, link = ref.split('\\"')
					sentence.strip('\\"')
					ref = sentence + link
					if ref:
						references.append(ref)

			combined_output = {
				"course_title": f"Introduction to {topic}",
				"description": f"A comprehensive introduction to {topic.lower()}, designed for {target_audience.lower()} with no prior knowledge.",
				"modules": [],
				"references": references,
			}

			for module in modules:
				module_dict = {"title": module["title"], "lessons": []}
				lesson: dict[str, Any]
				for i, lesson in enumerate(module["lessons"]):
					existing_resources = lesson.get("resources", [])
					resources = (
						visuals.get(lesson["title"], [])[i : i + 1]
						if i
						< len(
							visuals.get(lesson["title"], []),
						)
						else []
					)
					lesson_dict = {
						"title": lesson.get("title", f"Untitled Lesson {i + 1}"),
						"content": lesson.get("content", ""),
						"resources": existing_resources + resources if resources else existing_resources,
					}
					module_dict["lessons"].append(lesson_dict)
				combined_output["modules"].append(module_dict)

			logger.debug(f"Final combined output:\n{combined_output}")
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

	async def run(self, brief: str, target_audience: str) -> dict[str, Any]:
		"""Run the orchestrator to generate a course from a description."""
		initial_state: State = {
			"initial_input": [
				HumanMessage(
					content=f"Brief: {brief} - Target Audience: {target_audience}",
				),
			],
			"research_summary": None,
			"filtered_modules": None,
			"organized_content": None,
			"visual_content": None,
			"final_course": None,
		}
		result = await self.graph.ainvoke(initial_state)
		return result["final_course"]


orchestrator = Orchestrator()
