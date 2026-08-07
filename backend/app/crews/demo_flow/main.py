#!/usr/bin/env python
from pathlib import Path

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
    def plan_content(self, crewai_trigger_payload: dict | None = None):
        if crewai_trigger_payload:
            self.state.topic = crewai_trigger_payload.get("topic", "AI Agents")
        else:
            self.state.topic = "AI Agents"

    @listen(plan_content)
    def generate_content(self):
        result = ContentCrew().crew().kickoff(inputs={"topic": self.state.topic})

        self.state.final_post = result.raw

    @listen(generate_content)
    def save_content(self):
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        with open(output_dir / "post.md", "w") as f:
            f.write(self.state.final_post)


def kickoff(inputs: dict | None = None):
    """Run the content flow with an optional trigger payload."""
    content_flow = ContentFlow()
    payload = {"crewai_trigger_payload": inputs} if inputs else {}
    return content_flow.kickoff(payload)


def plot():
    content_flow = ContentFlow()
    content_flow.plot()


def run_with_trigger():
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

    content_flow = ContentFlow()

    try:
        result = content_flow.kickoff({"crewai_trigger_payload": trigger_payload})
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the flow with trigger: {e}")


if __name__ == "__main__":
    kickoff()
