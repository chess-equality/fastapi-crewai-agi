#!/usr/bin/env python
from pathlib import Path
from typing import Any

from crewai import CrewOutput
from crewai.flow import Flow, listen, start
from pydantic import BaseModel

from app.crews.demo_flow.crews.content_crew.content_crew import ContentCrew


class ContentState(BaseModel):
    topic: str = ""
    outline: str = ""
    draft: str = ""
    final_post: str = ""


class ContentFlow(Flow[ContentState]):
    @start()
    def plan_content(
        self, crewai_trigger_payload: dict[str, Any] | None = None
    ) -> None:
        if crewai_trigger_payload:
            self.state.topic = crewai_trigger_payload.get("topic", "AI Agents")
        else:
            self.state.topic = "AI Agents"

    @listen(plan_content)
    def generate_content(self) -> None:
        result = ContentCrew().crew().kickoff(inputs={"topic": self.state.topic})
        if isinstance(result, CrewOutput):
            self.state.final_post = result.raw
        else:
            raise TypeError("Streaming output is not supported by this flow step")

    @listen(generate_content)
    def save_content(self) -> None:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        with open(output_dir / "post.md", "w") as f:
            f.write(self.state.final_post)


def kickoff(inputs: dict[str, Any] | None = None) -> Any:
    """Run the content flow with an optional trigger payload."""
    # `Flow`'s pydantic-generated model declares `name`/`state` as fields, but its
    # actual `__init__(self, /, **data)` (verified via inspect.signature) takes no
    # required arguments at runtime — ty's static model doesn't see through that.
    content_flow = ContentFlow()  # ty: ignore[missing-argument]
    payload = {"crewai_trigger_payload": inputs} if inputs else {}
    return content_flow.kickoff(payload)


def plot() -> None:
    content_flow = ContentFlow()  # ty: ignore[missing-argument]
    content_flow.plot()


def run_with_trigger() -> Any:
    """
    Run the flow with trigger payload.
    """
    import json
    import sys

    if len(sys.argv) < 2:
        raise Exception(
            "No trigger payload provided. Please provide JSON payload as argument."
        )

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    content_flow = ContentFlow()  # ty: ignore[missing-argument]

    try:
        result = content_flow.kickoff({"crewai_trigger_payload": trigger_payload})
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the flow with trigger: {e}")


if __name__ == "__main__":
    kickoff()
