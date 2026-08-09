from typing import Any, ClassVar

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class ContentCrew:
    """Content Crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    # @CrewBase loads these YAML paths and replaces the attribute with the parsed mapping.
    agents_config: ClassVar[Any] = "config/agents.yaml"
    tasks_config: ClassVar[Any] = "config/tasks.yaml"

    # NOTE on the suppressions below: `Agent`/`Task` declare `role`/`goal`/`backstory`
    # and `description`/`expected_output` as required pydantic fields with no default.
    # A `@model_validator(mode="before")` (`process_config`) populates them from the
    # `config=` mapping at runtime — a documented CrewAI pattern — but neither checker's
    # static model of the constructor sees through that validator, so both flag the call
    # as missing required arguments. ty reports it as one `missing-argument` per call;
    # mypy additionally reports it as `call-arg` for `Task` (but not `Agent`).

    @agent
    def planner(self) -> Agent:
        return Agent(config=self.agents_config["planner"])  # ty: ignore[missing-argument]

    @agent
    def writer(self) -> Agent:
        return Agent(config=self.agents_config["writer"])  # ty: ignore[missing-argument]

    @agent
    def editor(self) -> Agent:
        return Agent(config=self.agents_config["editor"])  # ty: ignore[missing-argument]

    @task
    def planning_task(self) -> Task:
        return Task(config=self.tasks_config["planning_task"])  # type: ignore[call-arg]  # ty: ignore[missing-argument]

    @task
    def writing_task(self) -> Task:
        return Task(config=self.tasks_config["writing_task"])  # type: ignore[call-arg]  # ty: ignore[missing-argument]

    @task
    def editing_task(self) -> Task:
        return Task(config=self.tasks_config["editing_task"])  # type: ignore[call-arg]  # ty: ignore[missing-argument]

    @crew
    def crew(self) -> Crew:
        """Creates the Content Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
