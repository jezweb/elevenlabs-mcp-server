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
from pathlib import Path
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

# Import all tools
from tools import (
    # Test Management
    list_tests,
    get_test,
    create_test,
    update_test,
    delete_test,
    get_test_summaries,
    # Test Execution
    run_tests_on_agent,
    get_test_invocation,
    resubmit_test,
    # Simulation
    simulate_conversation,
    stream_simulate_conversation
)

# Setup logging
logger = setup_logging(__name__)

# Validate configuration
if not Config.API_KEY:
    logger.error("ELEVENLABS_API_KEY not set")
    sys.exit(1)

# Initialize ElevenLabs client at module level
client = ElevenLabsClient(Config.API_KEY)

# Load resources
def load_resource(filename: str) -> Dict[str, Any]:
    """Load a JSON resource file with proper error handling."""
    resource_path = Path(__file__).parent / "resources" / filename
    try:
        if not resource_path.exists():
            logger.error(f"Resource file not found: {resource_path}")
            return {}
        
        with open(resource_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Successfully loaded {filename}: {len(data)} items")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error in {filename}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error loading resource {filename}: {e}")
        return {}

# Load templates at module level for efficiency
TEST_TEMPLATES = load_resource("test_templates.json")
SCENARIO_TEMPLATES = load_resource("scenario_templates.json") 
VALIDATION_TEMPLATES = load_resource("validation_templates.json")

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


# ============================================================
# Test Management Tools
# ============================================================

@mcp.tool()
async def list_tests_tool(
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
    return await list_tests(client, agent_id, limit)


@mcp.tool()
async def get_test_tool(
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
    return await get_test(client, test_id)


@mcp.tool()
async def create_test_tool(
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
    return await create_test(client, name, agent_id, test_type, scenarios, expectations, metadata)


@mcp.tool()
async def update_test_tool(
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
    return await update_test(client, test_id, name, scenarios, expectations, metadata)


@mcp.tool()
async def delete_test_tool(
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
    return await delete_test(client, test_id)


@mcp.tool()
async def get_test_summaries_tool(
    test_ids: List[str]
) -> Dict[str, Any]:
    """
    Get batch test summaries.
    
    Args:
        test_ids: List of test IDs
    
    Returns:
        Summary statistics for tests
    """
    return await get_test_summaries(client, test_ids)


# ============================================================
# Test Execution Tools
# ============================================================

@mcp.tool()
async def run_tests_on_agent_tool(
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
    return await run_tests_on_agent(client, agent_id, test_ids, test_type, parallel)


@mcp.tool()
async def get_test_invocation_tool(
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
    return await get_test_invocation(client, invocation_id)


@mcp.tool()
async def resubmit_test_tool(
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
    return await resubmit_test(client, invocation_id, retry_failed_only)


# ============================================================
# Simulation Tools
# ============================================================

@mcp.tool()
async def simulate_conversation_tool(
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
    return await simulate_conversation(client, agent_id, user_message, context, max_turns)


@mcp.tool()
async def stream_simulate_conversation_tool(
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
    return await stream_simulate_conversation(client, agent_id, user_message, stream_callback)


# Resources

@mcp.resource(
    "resource://test-templates",
    name="ElevenLabs Testing Templates",
    description="Comprehensive templates for testing conversational AI agents including conversation tests, tool tests, integration tests, performance tests, and regression tests. Provides detailed test scenarios, success criteria, and validation frameworks for ensuring agent quality and reliability.",
    mime_type="application/json",
    tags={"testing", "templates", "validation", "quality_assurance", "conversation_tests"},
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True
    }
)
async def get_test_templates_resource() -> str:
    """Get agent testing templates as a JSON resource."""
    return json.dumps(TEST_TEMPLATES, indent=2)


@mcp.resource(
    "resource://scenario-templates", 
    name="ElevenLabs Test Scenarios",
    description="Pre-configured test scenarios for different conversation types including customer support, technical support, sales interactions, edge cases, and conversation flow patterns. Each scenario includes expected behaviors, success metrics, and validation criteria for comprehensive agent testing.",
    mime_type="application/json",
    tags={"scenarios", "test_cases", "customer_support", "technical_support", "conversation_flows"},
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True
    }
)
async def get_scenario_templates_resource() -> str:
    """Get test scenario templates as a JSON resource."""
    return json.dumps(SCENARIO_TEMPLATES, indent=2)


@mcp.resource(
    "resource://validation-templates",
    name="ElevenLabs Validation Framework",
    description="Quality validation frameworks for evaluating agent performance including response quality validation, conversation flow analysis, technical performance metrics, business outcome measurement, and compliance validation. Provides scoring rubrics, criteria definitions, and evaluation methodologies.",
    mime_type="application/json",
    tags={"validation", "quality_metrics", "performance", "compliance", "evaluation"},
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True
    }
)
async def get_validation_templates_resource() -> str:
    """Get validation framework templates as a JSON resource."""
    return json.dumps(VALIDATION_TEMPLATES, indent=2)


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