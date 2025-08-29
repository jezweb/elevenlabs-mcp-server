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
    expectations: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Create a new test scenario for agent validation.
    
    Args:
        name: Test name (str, descriptive)
            Example: "Customer greeting flow"
            
        agent_id: Agent to test (str, format: agent_XXXX)
            Example: "agent_8601k3tv9x6nf6trr3zw31mgtpre"
            
        test_type: Type of test (str, default: "conversation")
            Options: "conversation", "tool", "integration"
            
        scenarios: Test conversation flows (Optional[List[Dict]])
            IMPORTANT: Pass as a list of dictionaries, NOT a JSON string!
            
            ✓ CORRECT: scenarios=[{"input": "Hello", "expected": "greeting"}]
            ✗ WRONG:   scenarios='[{"input": "Hello"}]'  # Don't pass as string
            
            Scenario dict structure:
            - input: User message (str) - what the user says
            - expected: Expected response type (str) - e.g., "tool_usage", "greeting"
            - notes: Test notes (str, optional) - explanation of expectation
            - role: Speaker role (str, optional) - defaults to "user"
            
            Examples:
                [{"input": "Hi", "expected": "greeting"}]
                [
                    {"input": "Book a haircut", "expected": "tool_usage", 
                     "notes": "Should use list_appointments"},
                    {"input": "2pm please", "expected": "booking_confirmation"}
                ]
                
        expectations: Expected outcomes (Optional[Dict[str, Any]])
            IMPORTANT: Pass as a dictionary, NOT a JSON string!
            
            ✓ CORRECT: expectations={"must_use_tools": ["list_appointments"]}
            ✗ WRONG:   expectations='{"must_use_tools": []}'  # Don't pass as string
            
            Common keys:
            - must_use_tools: List[str] - tools that must be called
            - conversation_quality: str - e.g., "natural_flow", "professional"
            - privacy_compliance: bool - whether to check privacy
            - success_condition: str - custom success evaluation prompt
            - tool_call_parameters: Dict - for advanced tool testing config
            - dynamic_variables: Dict - for runtime variable substitution
            
            Examples:
                {"must_use_tools": ["list_appointments", "create_client"]}
                {"conversation_quality": "natural_flow", "privacy_compliance": true}
                {
                    "must_use_tools": ["list_appointments"],
                    "tool_call_parameters": {
                        "required_tools": ["list_appointments"],
                        "evaluation_mode": "strict"
                    }
                }
    
    Returns:
        Dict with created test details and test_id
    
    Usage Examples:
        # Simple test
        create_test_tool(
            name="Greeting Test",
            agent_id="agent_abc123"
        )
        
        # Complex test with scenarios and expectations (CORRECT way)
        create_test_tool(
            name="Booking Flow Test",
            agent_id="agent_xyz789",
            test_type="tool",
            scenarios=[  # List of dicts, not JSON string!
                {"input": "Book appointment", "expected": "tool_usage"},
                {"input": "Tomorrow 2pm", "expected": "confirmation"}
            ],
            expectations={  # Dict, not JSON string!
                "must_use_tools": ["list_appointments", "create_booking"],
                "conversation_quality": "professional",
                "tool_call_parameters": {
                    "required_tools": ["list_appointments", "create_booking"],
                    "evaluation_mode": "strict"
                }
            }
        )
    
    API Endpoint: POST /convai/agent-testing/create
    """
    return await create_test(client, name, agent_id, test_type, scenarios, expectations)


@mcp.tool()
async def update_test_tool(
    test_id: str,
    name: Optional[str] = None,
    scenarios: Optional[List[Dict]] = None,
    expectations: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Update existing test scenario configuration.
    
    Args:
        test_id: Test to update (str, format: test_XXXX)
            Example: "test_abc123def456"
            
        name: New test name (Optional[str])
            Example: "Updated Booking Flow Test"
            
        scenarios: Updated test flows (Optional[List[Dict]])
            IMPORTANT: Pass as a list of dictionaries, NOT a JSON string!
            
            ✓ CORRECT: scenarios=[{"input": "Hi", "expected": "greeting"}]
            ✗ WRONG:   scenarios='[{"input": "Hi"}]'  # Don't pass as string
            
            Same structure as create_test_tool:
            - input: User message (str)
            - expected: Expected response type (str)
            - notes: Test notes (str, optional)
            
            Example:
                [
                    {"input": "Update my booking", "expected": "tool_usage"},
                    {"input": "Change to 3pm", "expected": "confirmation"}
                ]
                
        expectations: Updated expected outcomes (Optional[Dict])
            IMPORTANT: Pass as a dictionary, NOT a JSON string!
            
            ✓ CORRECT: expectations={"must_use_tools": ["update_booking"]}
            ✗ WRONG:   expectations='{"must_use_tools": []}'  # Don't pass as string
            
            Same keys as create_test_tool:
            - must_use_tools: List[str]
            - conversation_quality: str
            - privacy_compliance: bool
            - success_condition: str
            - tool_call_parameters: Dict
            - dynamic_variables: Dict
    
    Returns:
        Dict with updated test configuration
    
    Usage Examples:
        # Update just the name
        update_test_tool(
            test_id="test_abc123",
            name="Updated Greeting Test"
        )
        
        # Update scenarios and expectations (CORRECT way)
        update_test_tool(
            test_id="test_xyz789",
            scenarios=[  # List of dicts, not JSON string!
                {"input": "Hi", "expected": "greeting"},
                {"input": "Help me book", "expected": "tool_usage"}
            ],
            expectations={  # Dict, not JSON string!
                "must_use_tools": ["list_appointments"],
                "conversation_quality": "friendly"
            }
        )
    
    API Endpoint: PUT /convai/agent-testing/{test_id}
    
    Note: Only provided fields are updated. Omitted fields remain unchanged.
    """
    return await update_test(client, test_id, name, scenarios, expectations)


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
        test_ids: List of test IDs (List[str])
            IMPORTANT: Pass as a Python list, NOT a JSON string!
            
            ✓ CORRECT: test_ids=["test_abc123", "test_xyz789"]
            ✗ WRONG:   test_ids='["test_abc123", "test_xyz789"]'  # Don't pass as string
            
            Example:
                ["test_abc123", "test_def456", "test_ghi789"]
    
    Returns:
        Dict with summary statistics for all specified tests
        
    Usage Example:
        get_test_summaries_tool(
            test_ids=["test_001", "test_002", "test_003"]  # List, not string!
        )
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
        agent_id: Agent to test (str, format: agent_XXXX)
            Example: "agent_8601k3tv9x6nf6trr3zw31mgtpre"
            
        test_ids: Specific tests to run (Optional[List[str]])
            IMPORTANT: Pass as a Python list, NOT a JSON string!
            
            ✓ CORRECT: test_ids=["test_001", "test_002"]
            ✗ WRONG:   test_ids='["test_001", "test_002"]'  # Don't pass as string
            
            Example:
                ["test_abc123", "test_def456"]
                
        test_type: Filter by type (Optional[str])
            Options: "conversation", "tool", "integration"
            Example: "conversation"
            
        parallel: Run tests concurrently (bool, default: False)
            - False: Sequential execution, easier debugging
            - True: Parallel execution, faster but may hit rate limits
    
    Returns:
        Dict with test execution results and invocation_id for tracking
    
    Usage Examples:
        # Run all tests for an agent
        run_tests_on_agent_tool(
            agent_id="agent_abc123"
        )
        
        # Run specific tests (CORRECT way)
        run_tests_on_agent_tool(
            agent_id="agent_xyz789",
            test_ids=["test_001", "test_002"]  # List, not string!
        )
        
        # Run tests by type with parallel execution
        run_tests_on_agent_tool(
            agent_id="agent_def456",
            test_type="conversation",
            parallel=True
        )
    
    API Endpoint: POST /convai/agents/{agent_id}/run-tests
    
    Note: Use get_test_invocation_tool() with returned invocation_id to check results.
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
            Example: "agent_8601k3tv9x6nf6trr3zw31mgtpre"
            
        user_message: Initial user input to start conversation (string)
            Example: "Hi, I'd like to book a haircut for tomorrow"
            
        context: Conversation context/variables (Optional[Dict[str, Any]])
            IMPORTANT: Pass as a Python dictionary, NOT a JSON string!
            
            ✓ CORRECT: context={"location": "Dublin", "time": "afternoon"}
            ✗ WRONG:   context='{"location": "Dublin"}'  # Don't pass as string
            
            Common context keys:
            - location: User's location (str) - e.g., "Dublin", "NYC"
            - time: Time context (str) - e.g., "morning", "afternoon", "evening"
            - user_name: User's name (str) - e.g., "John", "Sarah"
            - service: Service type (str) - e.g., "haircut", "booking"
            - preferences: User preferences (dict) - e.g., {"style": "modern"}
            
            Examples:
                {"location": "NYC", "time": "evening"}
                {"user_name": "John", "preference": "quiet"}
                {"service": "haircut", "day": "tomorrow"}
                
        max_turns: Maximum conversation turns (int, 1-50, default: 10)
            Example: 10
    
    Returns:
        Dict containing simulated conversation with analysis
    
    Usage Examples:
        # Simple simulation
        simulate_conversation_tool(
            agent_id="agent_abc123",
            user_message="Hello, I need help"
        )
        
        # With context (CORRECT way)
        simulate_conversation_tool(
            agent_id="agent_xyz789",
            user_message="I want to order pizza",
            context={"location": "NYC", "time": "evening"},  # Dict, not string!
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