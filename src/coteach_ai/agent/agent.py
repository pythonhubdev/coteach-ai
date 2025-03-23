import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from loguru import logger

from .config.constants import State


class Agent(ABC):
	"""Base class for all agents in the system."""

	def __init__(self, agent_id: str):
		self.agent_id = agent_id
		self.status = "initialized"
		self.start_time: datetime = datetime.now()
		self.end_time: datetime | None = None
		self.execution_time: float | None = None
		self.retry_count = 0
		self.max_retries = 3

	async def run(self, input_data: State) -> dict[str, Any]:
		"""Execute the agent's main functionality."""
		self.status = "running"
		self.start_time = datetime.now()

		try:
			result = await self.execute(input_data)
			self.status = "completed"
			self.end_time = datetime.now()
			self.execution_time = (self.end_time - self.start_time).total_seconds()
			logger.info(f"Execution time: {self.execution_time}")
			return result
		except Exception as exception:
			self.status = "failed"
			self.end_time = datetime.now()
			self.execution_time = (self.end_time - self.start_time).total_seconds()
			if self.retry_count < self.max_retries:
				self.retry_count += 1
				logger.warning(f"Agent {self.agent_id} failed, retrying... ({self.retry_count}/{self.max_retries})")
				await asyncio.sleep(2**self.retry_count)
				return await self.run(input_data)
			logger.error(f"Agent {self.agent_id} failed after {self.max_retries} retries")
			raise exception

	@abstractmethod
	async def execute(self, input_data: State) -> dict[str, Any]:
		"""Abstract method to be implemented by specific agents."""
