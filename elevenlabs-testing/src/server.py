"""ElevenLabs Testing MCP Server.

Provides tools for testing agents and running simulations.
"""

import asyncio
import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Literal

from fastmcp import FastMCP

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import (
    Config,
    ElevenLabsClient,
    format_error,
    format_success,
    validate_elevenlabs_id,
    setup_logging
)

# Setup logging
logger = setup_logging(__name__)

# Validate configuration
if not Config.API_KEY:
    logger.error("ELEVENLABS_API_KEY not set")
    sys.exit(1)

# Initialize ElevenLabs client at module level
client = ElevenLabsClient(Config.API_KEY)

# Initialize FastMCP server
mcp = FastMCP(
    name="elevenlabs-testing",
    instructions="Test and simulate ElevenLabs conversational AI agents"
)


@asynccontextmanager
async def lifespan(app):
    """Lifespan context manager for the MCP server."""
    # Startup
    logger.info("Starting ElevenLabs Testing MCP server")
    
    # Test connection
    if not await client.test_connection():
        logger.error("Failed to connect to ElevenLabs API")
        logger.warning("Some features may be unavailable")
    else:
        logger.info("ElevenLabs API connection verified")
    
    logger.info("ElevenLabs Testing MCP server started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ElevenLabs Testing MCP server")
    if client:
        await client.close()


# Set lifespan
mcp.lifespan = lifespan


# Test Management Tools

@mcp.tool()
async def list_tests(
    agent_id: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    List all available test scenarios for agents.
    
    Args:
        agent_id: Filter by specific agent (optional, format: agent_XXXX)
        limit: Maximum results (1-100, default: 50)
    
    Returns:
        List of test scenarios with metadata
    
    Examples:
        list_tests()  # All tests
        list_tests("agent_abc123")  # Tests for specific agent
        list_tests(limit=100)  # Get more results
    
    API Endpoint: GET /convai/tests
    """
    # Validate agent ID if provided
    if agent_id:
        if not validate_elevenlabs_id(agent_id, 'agent'):
            return format_error(
                f"Invalid agent ID format: {agent_id}",
                "Use format: agent_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
            )
    
    # Validate and coerce limit
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        return format_error(
            "Limit must be an integer",
            "Provide a number between 1 and 100"
        )
    
    if limit < 1:
        return format_error(
            f"Limit too low: {limit}",
            "Minimum is 1 test"
        )
    elif limit > 100:
        return format_error(
            f"Limit too high: {limit}",
            "Maximum is 100 tests per request"
        )
    
    try:
        params = {"limit": limit}
        if agent_id:
            params["agent_id"] = agent_id
        
        result = await client._request(
            "GET",
            "/convai/agent-testing",
            params=params,
            use_cache=True
        )
        
        tests = result.get("tests", [])
        
        return format_success(
            f"Found {len(tests)} test scenarios",
            {"tests": tests, "count": len(tests)}
        )
        
    except Exception as e:
        logger.error(f"Failed to list tests: {e}")
        return format_error(str(e))


@mcp.tool()
async def get_test(
    test_id: str
) -> Dict[str, Any]:
    """
    Get detailed test scenario configuration.
    
    Args:
        test_id: Test scenario ID (format: test_XXXX)
    
    Returns:
        Complete test configuration with steps and expectations
    
    Examples:
        get_test("test_abc123")
    
    API Endpoint: GET /convai/tests/{test_id}
    
    Test Configuration Includes:
        - Test metadata (name, description, tags)
        - Input scenarios and prompts
        - Expected responses and behaviors
        - Success criteria and thresholds
        - Validation rules
    """
    # Validate test ID
    if not test_id:
        return format_error(
            "Test ID is required",
            "Provide test_id from list_tests()"
        )
    
    if not validate_elevenlabs_id(test_id, 'test'):
        return format_error(
            f"Invalid test ID format: {test_id}",
            "Use format: test_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        )
    
    try:
        result = await client._request(
            "GET",
            f"/convai/agent-testing/{test_id}",
            use_cache=True
        )
        
        return format_success(
            "Retrieved test scenario",
            {"test": result}
        )
        
    except Exception as e:
        logger.error(f"Failed to get test {test_id}: {e}")
        return format_error(str(e))


@mcp.tool()
async def create_test(
    name: str,
    agent_id: str,
    test_type: Literal["conversation", "tool", "integration"] = "conversation",
    scenarios: List[Dict[str, Any]] = None,
    expectations: Dict[str, Any] = None,
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Create a new test scenario for agent validation.
    
    Args:
        name: Test name (descriptive, e.g., "Customer greeting flow")
        agent_id: Agent to test (format: agent_XXXX)
        test_type: Type of test
            - "conversation": Test dialogue flows
            - "tool": Test tool/function calls
            - "integration": Test external integrations
        scenarios: Test conversation flows (list of interaction steps)
        expectations: Expected outcomes (response patterns, behaviors)
        metadata: Additional metadata (tags, priority, etc.)
    
    Returns:
        Created test with ID and configuration
    
    Examples:
        create_test(
            "Greeting Test",
            "agent_abc123",
            "conversation",
            scenarios=[{"input": "Hello", "expected": "greeting"}]
        )
    
    API Endpoint: POST /convai/tests
    """
    # Validate inputs
    if not name or not name.strip():
        return format_error(
            "Test name cannot be empty",
            "Provide a descriptive name like 'Customer Support Flow' or 'Order Processing Test'"
        )
    
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error(
            f"Invalid agent ID format: {agent_id}",
            "Use format: agent_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        )
    
    try:
        data = {
            "name": name,
            "agent_id": agent_id,
            "type": test_type,
            "scenarios": scenarios or [],
            "expectations": expectations or {},
            "metadata": metadata or {}
        }
        
        result = await client._request(
            "POST",
            "/convai/agent-testing/create",
            json_data=data
        )
        
        return format_success(
            f"Created test scenario '{name}'",
            {"test": result}
        )
        
    except Exception as e:
        logger.error(f"Failed to create test: {e}")
        return format_error(str(e))


@mcp.tool()
async def update_test(
    test_id: str,
    name: Optional[str] = None,
    scenarios: Optional[List[Dict]] = None,
    expectations: Optional[Dict] = None,
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Update existing test scenario configuration.
    
    Args:
        test_id: Test to update (format: test_XXXX)
        name: New test name (optional)
        scenarios: Updated test flows (optional)
        expectations: Updated expected outcomes (optional)
        metadata: Updated metadata (optional)
    
    Returns:
        Updated test configuration
    
    Examples:
        update_test("test_abc123", name="Updated Greeting Test")
        update_test(
            "test_xyz789",
            scenarios=[{"input": "Hi", "expected": "greeting"}]
        )
    
    API Endpoint: PUT /convai/tests/{test_id}
    
    Note: Only provided fields are updated. Omitted fields remain unchanged.
    """
    # Validate test ID
    if not test_id:
        return format_error(
            "Test ID is required",
            "Provide test_id from list_tests() or get_test()"
        )
    
    if not validate_elevenlabs_id(test_id, 'test'):
        return format_error(
            f"Invalid test ID format: {test_id}",
            "Use format: test_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        )
    
    try:
        data = {}
        if name:
            data["name"] = name
        if scenarios is not None:
            data["scenarios"] = scenarios
        if expectations is not None:
            data["expectations"] = expectations
        if metadata is not None:
            data["metadata"] = metadata
        
        result = await client._request(
            "PUT",
            f"/convai/agent-testing/{test_id}",
            json_data=data
        )
        
        return format_success(
            f"Updated test {test_id}",
            {"test": result}
        )
        
    except Exception as e:
        logger.error(f"Failed to update test {test_id}: {e}")
        return format_error(str(e))


@mcp.tool()
async def delete_test(
    test_id: str
) -> Dict[str, Any]:
    """
    Delete test scenario permanently.
    
    Args:
        test_id: Test to delete (format: test_XXXX)
    
    Returns:
        Deletion confirmation
    
    Examples:
        delete_test("test_abc123")
    
    API Endpoint: DELETE /convai/tests/{test_id}
    
    Warning: This action is permanent and cannot be undone.
    """
    # Validate test ID
    if not test_id:
        return format_error(
            "Test ID is required",
            "Provide test_id from list_tests()"
        )
    
    if not validate_elevenlabs_id(test_id, 'test'):
        return format_error(
            f"Invalid test ID format: {test_id}",
            "Use format: test_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        )
    
    try:
        await client._request(
            "DELETE",
            f"/convai/agent-testing/{test_id}"
        )
        
        return format_success(
            f"Deleted test {test_id}",
            {"deleted": True}
        )
        
    except Exception as e:
        logger.error(f"Failed to delete test {test_id}: {e}")
        return format_error(str(e))


@mcp.tool()
async def get_test_summaries(
    test_ids: List[str]
) -> Dict[str, Any]:
    """
    Get batch test summaries.
    
    Args:
        test_ids: List of test IDs
    
    Returns:
        Summary statistics for tests
    """
    try:
        for test_id in test_ids:
            if not validate_elevenlabs_id(test_id, 'test'):
                return format_error(f"Invalid test ID format: {test_id}")
        
        result = await client._request(
            "POST",
            "/convai/agent-testing/summaries",
            json_data={"test_ids": test_ids}
        )
        
        return format_success(
            f"Retrieved summaries for {len(test_ids)} tests",
            {"summaries": result.get("summaries", [])}
        )
        
    except Exception as e:
        logger.error(f"Failed to get test summaries: {e}")
        return format_error(str(e))


# Test Execution Tools

@mcp.tool()
async def run_tests_on_agent(
    agent_id: str,
    test_ids: Optional[List[str]] = None,
    test_type: Optional[str] = None,
    parallel: bool = False
) -> Dict[str, Any]:
    """
    Execute comprehensive test suite on an agent.
    
    Args:
        agent_id: Agent to test (format: agent_XXXX)
        test_ids: Specific tests to run (optional list)
        test_type: Filter by type ("conversation", "tool", "integration")
        parallel: Run tests concurrently (default: False)
            - False: Sequential execution, easier debugging
            - True: Parallel execution, faster but may hit rate limits
    
    Returns:
        Test execution results with invocation ID for tracking
    
    Examples:
        run_tests_on_agent("agent_abc123")  # Run all tests
        run_tests_on_agent("agent_xyz789", test_ids=["test_001", "test_002"])
        run_tests_on_agent("agent_def456", test_type="conversation", parallel=True)
    
    API Endpoint: POST /convai/agents/{agent_id}/run-tests
    
    Note: Use get_test_invocation() with returned invocation_id to check results.
    """
    # Validate agent ID
    if not agent_id:
        return format_error(
            "Agent ID is required",
            "Provide agent_id to test"
        )
    
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error(
            f"Invalid agent ID format: {agent_id}",
            "Use format: agent_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        )
    
    try:
        if test_ids:
            for test_id in test_ids:
                if not validate_elevenlabs_id(test_id, 'test'):
                    return format_error(f"Invalid test ID format: {test_id}")
        
        data = {
            "test_ids": test_ids,
            "test_type": test_type,
            "parallel": parallel
        }
        
        result = await client._request(
            "POST",
            f"/convai/agents/{agent_id}/run-tests",
            json_data=data
        )
        
        return format_success(
            f"Executed tests on agent {agent_id}",
            {
                "invocation_id": result.get("invocation_id"),
                "status": result.get("status"),
                "results": result.get("results", [])
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to run tests on agent {agent_id}: {e}")
        return format_error(str(e))


@mcp.tool()
async def get_test_invocation(
    invocation_id: str
) -> Dict[str, Any]:
    """
    Get detailed test execution results and status.
    
    Args:
        invocation_id: Test invocation ID (format: inv_XXXX)
    
    Returns:
        Complete test results with pass/fail status
    
    Examples:
        get_test_invocation("inv_abc123")
    
    API Endpoint: GET /convai/test-invocations/{invocation_id}
    
    Results Include:
        - Overall status (running, completed, failed)
        - Individual test results
        - Pass/fail counts
        - Error messages and stack traces
        - Execution duration
        - Detailed logs per test
    """
    # Validate invocation ID
    if not invocation_id:
        return format_error(
            "Invocation ID is required",
            "Provide invocation_id from run_tests_on_agent()"
        )
    
    if not validate_elevenlabs_id(invocation_id, 'invocation'):
        return format_error(
            f"Invalid invocation ID format: {invocation_id}",
            "Use format: inv_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        )
    
    try:
        result = await client._request(
            "GET",
            f"/convai/test-invocations/{invocation_id}",
            use_cache=True
        )
        
        return format_success(
            "Retrieved test invocation results",
            {"invocation": result}
        )
        
    except Exception as e:
        logger.error(f"Failed to get test invocation {invocation_id}: {e}")
        return format_error(str(e))


@mcp.tool()
async def resubmit_test(
    invocation_id: str,
    retry_failed_only: bool = True
) -> Dict[str, Any]:
    """
    Retry failed test execution.
    
    Args:
        invocation_id: Previous invocation ID
        retry_failed_only: Only retry failed tests
    
    Returns:
        New invocation results
    """
    try:
        if not validate_elevenlabs_id(invocation_id, 'invocation'):
            return format_error("Invalid invocation ID format", "Use format: inv_XXXX")
        
        result = await client._request(
            "POST",
            f"/convai/test-invocations/{invocation_id}/resubmit",
            json_data={"retry_failed_only": retry_failed_only}
        )
        
        return format_success(
            "Resubmitted test invocation",
            {
                "new_invocation_id": result.get("invocation_id"),
                "status": result.get("status")
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to resubmit test {invocation_id}: {e}")
        return format_error(str(e))


# Simulation Tools

@mcp.tool()
async def simulate_conversation(
    agent_id: str,
    user_message: str,
    context: Optional[Dict] = None,
    max_turns: int = 10
) -> Dict[str, Any]:
    """
    Simulate a realistic conversation with an agent for testing.
    
    Args:
        agent_id: Agent to test (format: agent_XXXX)
        user_message: Initial user input to start conversation
        context: Conversation context/variables (optional)
            - user_name, location, preferences, etc.
        max_turns: Maximum conversation turns (1-50, default: 10)
    
    Returns:
        Complete simulated conversation with analysis
    
    Examples:
        simulate_conversation("agent_abc123", "Hello, I need help")
        simulate_conversation(
            "agent_xyz789",
            "I want to order pizza",
            context={"location": "NYC", "time": "evening"},
            max_turns=20
        )
    
    API Endpoint: POST /convai/agents/{agent_id}/simulate-conversation
    
    Use Cases:
        - Test agent responses without real conversations
        - Validate conversation flows
        - Debug agent behavior
        - Generate sample interactions
    """
    # Validate agent ID
    if not agent_id:
        return format_error(
            "Agent ID is required",
            "Provide agent_id to simulate conversation with"
        )
    
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error(
            f"Invalid agent ID format: {agent_id}",
            "Use format: agent_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        )
    
    # Validate user message
    if not user_message or not user_message.strip():
        return format_error(
            "User message cannot be empty",
            "Provide an initial message to start the conversation"
        )
    
    # Validate and coerce max_turns
    try:
        max_turns = int(max_turns)
    except (TypeError, ValueError):
        return format_error(
            "Max turns must be an integer",
            "Provide a number between 1 and 50"
        )
    
    if max_turns < 1:
        return format_error(
            f"Max turns too low: {max_turns}",
            "Minimum is 1 turn"
        )
    elif max_turns > 50:
        return format_error(
            f"Max turns too high: {max_turns}",
            "Maximum is 50 turns to prevent excessive simulation"
        )
    
    try:
        data = {
            "simulation_specification": {
                "simulated_user_config": {
                    "first_message": user_message,
                    "language": "en"
                }
            }
        }
        
        # Add context if provided
        if context:
            data["simulation_specification"]["context"] = context
            
        # Add max_turns if specified
        if max_turns != 10:  # Only include if different from default
            data["simulation_specification"]["max_turns"] = max_turns
        
        result = await client._request(
            "POST",
            f"/convai/agents/{agent_id}/simulate-conversation",
            json_data=data
        )
        
        return format_success(
            "Simulated conversation completed",
            {
                "conversation": result.get("conversation"),
                "turns": result.get("turns"),
                "duration": result.get("duration")
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to simulate conversation for {agent_id}: {e}")
        return format_error(str(e))


@mcp.tool()
async def stream_simulate_conversation(
    agent_id: str,
    user_message: str,
    stream_callback: Optional[str] = None
) -> Dict[str, Any]:
    """
    Stream conversation simulation in real-time.
    
    Args:
        agent_id: Agent to test
        user_message: Initial message
        stream_callback: Webhook for streaming
    
    Returns:
        Stream session details
    """
    try:
        if not validate_elevenlabs_id(agent_id, 'agent'):
            return format_error("Invalid agent ID format", "Use format: agent_XXXX")
        
        data = {
            "message": user_message,
            "stream_callback": stream_callback
        }
        
        result = await client._request(
            "POST",
            f"/convai/agents/{agent_id}/stream-simulate-conversation",
            json_data=data
        )
        
        return format_success(
            "Started streaming simulation",
            {
                "session_id": result.get("session_id"),
                "stream_url": result.get("stream_url"),
                "status": "streaming"
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to stream simulation for {agent_id}: {e}")
        return format_error(str(e))


# Resources

@mcp.resource("resource://documentation")
async def get_documentation() -> str:
    """Get server documentation."""
    return """
# ElevenLabs Testing MCP Server

Comprehensive testing and simulation framework for ElevenLabs agents.

## Features

### Test Management
- Create and manage test scenarios
- Define conversation flows and expectations
- Support for different test types (conversation, tool, integration)

### Test Execution
- Run test suites on agents
- Parallel test execution
- Retry failed tests
- Get detailed execution results

### Simulation
- Simulate conversations with agents
- Stream real-time simulations
- Test agent responses without production impact

## Tool Categories

### Test Management Tools
- list_tests: Browse test scenarios
- get_test: Get test details
- create_test: Create new test scenario
- update_test: Modify test configuration
- delete_test: Remove test scenario
- get_test_summaries: Batch test statistics

### Execution Tools
- run_tests_on_agent: Execute test suite
- get_test_invocation: Get execution results
- resubmit_test: Retry failed tests

### Simulation Tools
- simulate_conversation: Run conversation simulation
- stream_simulate_conversation: Real-time simulation

## Usage Examples

### Create Test Scenario
```python
create_test(
    name="Customer Support Test",
    agent_id="agent_xyz789",
    test_type="conversation",
    scenarios=[
        {
            "user": "I need help with my order",
            "expected_response": "greeting and offer to help"
        }
    ],
    expectations={
        "response_time": "<2s",
        "sentiment": "positive"
    }
)
```

### Run Test Suite
```python
run_tests_on_agent(
    agent_id="agent_xyz789",
    test_ids=["test_abc123", "test_def456"],
    parallel=True
)
```

### Simulate Conversation
```python
simulate_conversation(
    agent_id="agent_xyz789",
    user_message="Hello, I have a question",
    max_turns=10
)
```

## Test Types

### Conversation Tests
Test agent responses to specific user inputs

### Tool Tests
Verify agent tool usage and integrations

### Integration Tests
Test end-to-end workflows with external systems
"""


# Entry point
if __name__ == "__main__":
    import sys
    
    # Check for test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("✅ ElevenLabs Testing MCP server initialized successfully")
        sys.exit(0)
    
    # Run the server
    mcp.run()