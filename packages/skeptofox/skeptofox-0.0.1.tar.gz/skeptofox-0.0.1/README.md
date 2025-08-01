# skeptofox

![PyPI - Version](https://img.shields.io/pypi/v/skeptofox)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/skeptofox)
![License](https://img.shields.io/pypi/l/skeptofox)

skeptofox provides a powerful, declarative paradigm for designing, building, and analyzing complex systems where human insight and machine intelligence collaborate. Define your *what*, and let Skeptofox orchestrate the *how*.


### Key Features

* **Declarative by Design:** Define complex workflows with intuitive, human-readable abstractions instead of writing brittle, imperative code.
* **Agentic AI Primitives:** High-level abstractions for bundling and linking single or multi-agent systems with data and automation pipelines.
* **Human-in-the-Loop:** Built-in hooks for human validation, feedback, and interactive steering of automated processes.
* **Extensible & Composable:** Easily integrate custom tools, models, data sources and endpoints from other pipelines into this self-orchestrating framework.

### Installation

```bash
pip install skeptofox
```

### Quick Start

Here's a simple example of defining a research agent that drafts a report and asks for human approval before finalizing it.

```python
from skeptofox import Workflow, Agent, HumanValidationStep, tool

# Define a simple tool for the agent to use
@tool
def web_search(query: str) -> str:
    """Performs a web search and returns the top results."""
    # (Your search implementation here)
    print(f"--> Searching for: {query}")
    return "Skeptofox was created in 2025. It focuses on declarative AI."

# 1. Define the Agent's identity and tools
researcher = Agent(
    role="Expert Tech Analyst",
    goal="Find information about the Skeptofox library and draft a summary.",
    tools=[web_search]
)

# 2. Declaratively define the workflow
wf = Workflow(
    name="Tech Report Workflow",
    steps=[
        researcher.plan("Create a plan to research Skeptofox."),
        researcher.execute("Execute the research plan."),
        HumanValidationStep(
            prompt="Please review the draft summary. Approve or provide feedback."
        ),
        researcher.execute("Finalize the report based on human feedback."),
    ],
)

# 3. Run the workflow
if __name__ == "__main__":
    final_report = wf.run()
    print("\n--- Final Report ---")
    print(final_report)
```

### Documentation

For detailed guides and API references, please see our full documentation (link coming soon).

### Contributing

Contributions are welcome! Whether it's bug reports, feature requests, or new code, please see our `CONTRIBUTING.md` guide for details on how to get started.

### License

This project is licensed under the MIT License. See the `LICENSE` file for details.