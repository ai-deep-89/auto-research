"""Multi-agent collaboration demo."""

import asyncio
from src.core.multi_agent import MultiAgentCrew, CollaborationMode
from src.agents.researcher import ResearcherAgent
from src.agents.planner import PlannerAgent
from src.agents.executor import ExecutorAgent
from src.agents.reviewer import ReviewerAgent


async def main():
    """Demonstrate multi-agent collaboration."""
    print("=" * 60)
    print("Multi-Agent Collaboration Demo")
    print("=" * 60)

    # Create agents
    print("\n[1] Creating specialized agents...")
    researcher = ResearcherAgent(name="researcher")
    planner = PlannerAgent(name="planner")
    executor = ExecutorAgent(name="executor")
    reviewer = ReviewerAgent(name="reviewer")

    agents = [researcher, planner, executor, reviewer]

    # Demonstrate different collaboration modes
    modes = [
        CollaborationMode.SEQUENTIAL,
        CollaborationMode.PARALLEL,
        CollaborationMode.HIERARCHICAL,
    ]

    task = "Research and compare multi-agent frameworks for autonomous research"

    for mode in modes:
        print(f"\n{'=' * 60}")
        print(f"Testing mode: {mode.value}")
        print(f"{'=' * 60}")

        # Create crew with specific mode
        crew = MultiAgentCrew(agents=agents, mode=mode)

        # Execute task
        result = await crew.run_async(task)

        # Display results
        print(f"\nResults:")
        print(f"  Success: {result.get('success', False)}")
        print(f"  Total Tasks: {result.get('total_tasks', 0)}")
        print(f"  Successful: {result.get('successful_tasks', 0)}")
        print(f"  Duration: {result.get('total_duration', 0):.2f}s")

        # Crew stats
        summary = crew.get_execution_summary()
        print(f"\nExecution Summary:")
        for agent_name, count in summary.get("by_agent", {}).items():
            print(f"  {agent_name}: {count} tasks")

    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
