import asyncio
import time
from tim_the_enchanter import (
    TimTheEnchanter,
    TimTheEnchanterReportFormat,
)


async def demonstrate_basic_usage():
    """Show basic usage of the performance tracker."""
    # Create a new tracker instance (request-scoped)
    tracker = TimTheEnchanter.create(enabled=True)
    
    # Start a new session and get the session ID
    session_id = tracker.start_session("demo_session")

    # Manual timing
    start = time.time()
    await asyncio.sleep(0.1)  # Simulate some work
    end = time.time()
    tracker.record(session_id, "manual_process", end - start)

    # Using context manager
    with tracker.time_process(session_id, "context_manager_process"):
        await asyncio.sleep(0.2)  # Simulate some work

    # Using decorator for sync function
    @tracker.time_function(session_id)
    def sync_function():
        time.sleep(0.15)  # Simulate some work

    sync_function()

    # Using decorator for async function
    @tracker.time_async_function(session_id)
    async def async_function():
        await asyncio.sleep(0.25)  # Simulate some work

    await async_function()

    # Print reports in different formats
    print("\n=== Chronological Report ===")
    tracker.print_report(session_id, TimTheEnchanterReportFormat.CHRONOLOGICAL)

    print("\n=== By Process Report ===")
    tracker.print_report(session_id, TimTheEnchanterReportFormat.BY_PROCESS)

    print("\n=== Aggregate Report ===")
    tracker.print_report(session_id, TimTheEnchanterReportFormat.AGGREGATE)

    # End the session
    tracker.end_session(session_id)


async def demonstrate_real_world_usage():
    """Demonstrate how to use the performance tracker in a real-world scenario."""
    # Create a new tracker instance for this request
    tracker = TimTheEnchanter.create(enabled=True)
    
    # Start a session for tracking a request
    session_id = tracker.start_session("document_processing")

    # Simulate document parsing
    with tracker.time_process(session_id, "document_parsing", {"doc_size": "2MB"}):
        await asyncio.sleep(0.3)  # Simulate parsing work

    # Simulate text embedding in multiple batches
    for i in range(3):
        with tracker.time_process(
            session_id, "text_embedding", {"batch": i, "model": "text-embedding-3-small"}
        ):
            # Different batches might take different times
            await asyncio.sleep(0.1 + (i * 0.05))

    # Simulate LLM processing
    with tracker.time_process(session_id, "llm_processing", {"model": "gpt-4"}):
        await asyncio.sleep(0.5)  # LLMs typically take longer

    # Simulate database operations
    with tracker.time_process(session_id, "database_operations"):
        for i in range(2):
            with tracker.time_process(
                session_id, "db_query", {"query_type": "vector_search"}
            ):
                await asyncio.sleep(0.1)

    # Generate an aggregate report
    tracker.print_report(session_id, TimTheEnchanterReportFormat.AGGREGATE)

    # End the session
    tracker.end_session(session_id)


async def demonstrate_multiple_requests():
    """Demonstrate how multiple requests can have isolated tracking."""
    print("\n=== Multiple Request Isolation Demo ===")
    
    # Simulate multiple concurrent requests
    async def handle_request(request_id: int):
        tracker = TimTheEnchanter.create(enabled=True)
        session_id = tracker.start_session(f"request_{request_id}")
        
        # Each request does different work
        with tracker.time_process(session_id, f"request_{request_id}_processing"):
            await asyncio.sleep(0.1 + (request_id * 0.05))
        
        # Get a quick report for this request
        report = tracker.report(session_id, TimTheEnchanterReportFormat.AGGREGATE)
        process_name = f"request_{request_id}_processing"
        print(f"Request {request_id} total time: {report['aggregates'][process_name]['total_time']:.3f}s")
        
        tracker.end_session(session_id)
        return tracker
    
    # Handle multiple requests concurrently
    trackers = await asyncio.gather(
        handle_request(1),
        handle_request(2),
        handle_request(3)
    )
    
    # Each tracker has its own isolated sessions
    for i, tracker in enumerate(trackers, 1):
        sessions = tracker.list_sessions()
        print(f"Tracker {i} sessions: {sessions}")


async def main():
    await demonstrate_basic_usage()
    print("\n" + "=" * 50 + "\n")
    await demonstrate_real_world_usage()
    print("\n" + "=" * 50 + "\n")
    await demonstrate_multiple_requests()


if __name__ == "__main__":
    asyncio.run(main())
