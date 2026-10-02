from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from brain.agents.base_agent import BaseAgent, response_text


class ReviewerAgent(BaseAgent):
	async def run(self, task: str, context: dict[str, Any]) -> str:
		response = await self.model.ainvoke([
			SystemMessage(
				content=(
					"You are a read-only software change reviewer. Inspect only the supplied "
					"proposal diff and evidence. Identify likely defects, scope drift, and "
					"checks that should be run. Do not modify files. Never state that tests "
					"passed unless explicit results are provided."
				)
			),
			HumanMessage(
				content=(
					f"User task:\n{task}\n\nProgrammer report:\n{context.get('programmer_report', '')}"
					f"\n\nProposed diff:\n{context.get('diffs', '')}"
				)
			),
		])
		return response_text(response)
