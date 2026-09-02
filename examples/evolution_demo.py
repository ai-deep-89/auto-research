"""Self-evolution demonstration."""

import asyncio
from src.evolution.evolution_engine import EvolutionEngine
from src.evolution.feedback import FeedbackType, FeedbackPriority
from src.agents.executor import ExecutorAgent


async def main():
    """Demonstrate agent self-evolution."""
    print("=" * 60)
    print("Agent Self-Evolution Demo")
    print("=" * 60)

    # Create an agent
    print("\n[1] Creating agent...")
    agent = ExecutorAgent(name="executor")

    # Create evolution engine
    print("[2] Initializing evolution engine...")
    engine = EvolutionEngine(
        max_iterations=5,
        convergence_threshold=0.02,
    )

    # Simulate feedback from multiple evaluations
    print("\n[3] Simulating feedback from evaluations...")

    feedback_history = [
        {
            "content": "Tool selection was incorrect for complex queries",
            "source": "reviewer",
            "success": False,
            "suggestions": ["Improve tool selection logic"],
            "task_id": "task_001",
        },
        {
            "content": "Code execution failed due to timeout",
            "source": "reviewer",
            "success": False,
            "suggestions": ["Add better timeout handling"],
            "task_id": "task_002",
        },
        {
            "content": "Good output structure and format",
            "source": "reviewer",
            "success": True,
            "suggestions": [],
            "task_id": "task_003",
        },
        {
            "content": "Improved tool accuracy this round",
            "source": "reviewer",
            "success": True,
            "suggestions": ["Continue refining tool selection"],
            "task_id": "task_004",
        },
    ]

    initial_metrics = {
        "task_success": 0.65,
        "tool_accuracy": 0.60,
        "collaboration": 0.75,
        "response_quality": 0.70,
    }

    print(f"\nInitial Metrics: {initial_metrics}")

    # Run evolution loop
    print("\n[4] Running evolution loop...")
    results = engine.evolve_multiple(
        agent=agent,
        feedback_history=feedback_history,
        metrics_history=[initial_metrics] * len(feedback_history),
    )

    # Display evolution progress
    print("\n" + "=" * 60)
    print("EVOLUTION RESULTS")
    print("=" * 60)

    for result in results:
        print(f"\nIteration {result.iteration}:")
        print(f"  Success: {result.success}")
        print(f"  Improvements: {result.improvement_score:.3f}")
        print(f"  Optimizations: {', '.join(result.optimizations_applied) or 'None'}")

        print(f"  Metrics Before: {result.metrics_before}")
        print(f"  Metrics After:  {result.metrics_after}")

    # Final summary
    print("\n" + "=" * 60)
    print("EVOLUTION SUMMARY")
    print("=" * 60)

    summary = engine.get_evolution_summary()
    for key, value in summary.items():
        if key != "evolution_trajectory":
            print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("Evolution demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
