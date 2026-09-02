"""Basic research task example."""

import asyncio
from src.core.system import AutoResearchSystem
from src.agents.researcher import ResearcherAgent
from src.agents.planner import PlannerAgent
from src.agents.executor import ExecutorAgent
from src.agents.reviewer import ReviewerAgent


async def main():
    """Run a basic research task."""
    print("=" * 60)
    print("AutoResearch Multi-Agent System - Basic Research Example")
    print("=" * 60)

    # Initialize agents
    print("\n[1] Initializing agents...")
    researcher = ResearcherAgent(name="researcher")
    planner = PlannerAgent(name="planner")
    executor = ExecutorAgent(name="executor")
    reviewer = ReviewerAgent(name="reviewer")

    # Create system
    print("[2] Creating AutoResearch system...")
    system = AutoResearchSystem(
        researcher=researcher,
        planner=planner,
        executor=executor,
        reviewer=reviewer,
        evolution_enabled=True,
    )

    # Define research task
    task = "Research the latest advances in LLM agent self-evolution techniques"

    print(f"\n[3] Executing research task:")
    print(f"    Task: {task}")

    # Execute research
    print("\n[4] Running multi-agent research pipeline...")
    result = await system.run_async(task, max_iterations=3)

    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    print(f"\nSuccess: {result.success}")
    print(f"Duration: {result.duration:.2f}s")
    print(f"Iterations: {result.iterations}")

    print("\n--- Output ---")
    if result.output:
        output = result.output
        print(f"Task Success: {output.get('successful_tasks', 0)}/{output.get('total_tasks', 0)}")
        if "review" in output:
            review = output["review"]
            print(f"Quality Score: {review.get('overall_quality_score', 0):.2f}")

    print("\n--- System Stats ---")
    stats = system.get_execution_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
