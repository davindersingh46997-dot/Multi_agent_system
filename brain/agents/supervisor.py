from collections.abc import Callable

from langchain_core.language_models import BaseChatModel

from brain.agents.image_analyst import ImageAnalyst
from brain.agents.programmer import ProgrammerAgent
from brain.agents.repository_analyst import RepositoryAnalyst
from brain.agents.tester import ReviewerAgent


class SupervisorAgent:
	def __init__(
		self,
		model: BaseChatModel,
		programmer: ProgrammerAgent,
		reviewer: ReviewerAgent,
	) -> None:
		self.repository_analyst = RepositoryAnalyst("Repository analyst", model)
		self.image_analyst = ImageAnalyst("Image analyst", model)
		self.programmer = programmer
		self.reviewer = reviewer

	async def run(
		self,
		task: str,
		retrieve_evidence: Callable[[str], str],
		images: list[tuple[str, bytes]],
		load_diffs: Callable[[], str],
	) -> str:
		image_notes = "No image attachment was provided."
		if images:
			image_notes = await self.image_analyst.run(task, {"images": images})
		evidence = retrieve_evidence(f"{task}\n{image_notes}")
		repository_notes = await self.repository_analyst.run(
			task, {"evidence": evidence}
		)

		working_context = (
			f"Repository analyst notes:\n{repository_notes}\n\n"
			f"Image analyst notes:\n{image_notes}\n\n"
			f"Retrieved project evidence:\n{evidence}"
		)
		programmer_report = await self.programmer.run(
			task, {"evidence": working_context}
		)
		diffs = load_diffs()
		review = "No file changes were proposed."
		if diffs:
			review = await self.reviewer.run(
				task,
				{"programmer_report": programmer_report, "diffs": diffs},
			)
		return (
			f"Repository analysis:\n{repository_notes}\n\n"
			f"Image analysis:\n{image_notes}\n\n"
			f"Retrieved project evidence:\n{evidence}\n\n"
			f"Programmer report:\n{programmer_report}\n\n"
			f"Reviewer notes:\n{review}\n\n"
			"No tests were run. Proposed changes require your approval before they are applied."
		)
