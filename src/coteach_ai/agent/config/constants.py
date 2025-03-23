from typing import TypedDict, Any

from langchain_core.messages import BaseMessage


class State(TypedDict):
	initial_input: list[BaseMessage]
	research_summary: str | None
	filtered_modules: str | None
	organized_content: str | None
	visual_content: str | None
	final_course: dict[str, Any] | None
