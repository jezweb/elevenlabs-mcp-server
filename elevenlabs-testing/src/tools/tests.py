"""
Test Management Tools
=====================
Tools for creating and managing test scenarios.
"""

import logging
from typing import Any, Dict, List, Optional, Literal

logger = logging.getLogger(__name__)


async def list_tests(
    client,
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
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
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


async def get_test(
    client,
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
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
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


async def create_test(
    client,
    name: str,
    agent_id: str,
    test_type: Literal["conversation", "tool", "integration"] = "conversation",
    scenarios: List[Dict[str, Any]] = None,
    expectations: Dict[str, Any] = None
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
    
    Returns:
        Created test with ID and configuration
    
    Examples:
        create_test(
            "Greeting Test",
            "agent_abc123",
            "conversation",
            scenarios=[{"input": "Hello", "expected": "greeting"}]
        )
    
    API Endpoint: POST /convai/agent-testing/create
    """
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
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
        # Transform scenarios into ElevenLabs chat_history format for test creation
        # NOTE: Test creation chat_history ONLY has role and time_in_call_secs, no message/content!
        chat_history = []
        if scenarios:
            time_counter = 1
            for scenario in scenarios:
                if isinstance(scenario, dict):
                    # For test creation, we only need role and time_in_call_secs
                    chat_history.append({
                        "role": scenario.get("role", "user"),
                        "time_in_call_secs": scenario.get("time_in_call_secs", time_counter)
                    })
                    # Add agent response placeholder if expected
                    if scenario.get("expected"):
                        time_counter += 1
                        chat_history.append({
                            "role": "assistant",
                            "time_in_call_secs": time_counter
                        })
                    time_counter += 1
        
        # Default chat history if none provided
        if not chat_history:
            chat_history = [{
                "role": "user",
                "time_in_call_secs": 1
            }]
        
        # Extract success condition and examples from expectations
        success_condition = "The agent should respond appropriately to the user's request"
        # NOTE: Examples ONLY have "response" field, not content/role!
        success_examples = [{"response": "Appropriate helpful response"}]
        failure_examples = [{"response": "Inappropriate or unhelpful response"}]
        
        if expectations:
            if "success_condition" in expectations:
                success_condition = expectations["success_condition"]
            elif "must_use_tools" in expectations:
                tools = ", ".join(expectations["must_use_tools"])
                success_condition = f"The agent should use the following tools: {tools}"
            
            if "success_examples" in expectations:
                # Ensure success_examples are in correct format (only "response" field)
                success_examples = []
                for example in expectations["success_examples"]:
                    if isinstance(example, dict):
                        if "response" in example:
                            success_examples.append({"response": example["response"]})
                        else:
                            # Convert any format to response-only format
                            success_examples.append({"response": str(example.get("content", example))})
                    else:
                        success_examples.append({"response": str(example)})
            elif "conversation_quality" in expectations:
                success_examples = [{
                    "response": f"Response demonstrates {expectations['conversation_quality']}"
                }]
            
            if "failure_examples" in expectations:
                # Ensure failure_examples are in correct format (only "response" field)
                failure_examples = []
                for example in expectations["failure_examples"]:
                    if isinstance(example, dict):
                        if "response" in example:
                            failure_examples.append({"response": example["response"]})
                        else:
                            # Convert any format to response-only format
                            failure_examples.append({"response": str(example.get("content", example))})
                    else:
                        failure_examples.append({"response": str(example)})
        
        # Build payload according to ElevenLabs API docs
        data = {
            "name": name,
            "chat_history": chat_history,
            "success_condition": success_condition,
            "success_examples": success_examples,
            "failure_examples": failure_examples
        }
        
        # Add optional parameters from expectations
        if expectations:
            # Allow tool_call_parameters to be passed directly in expectations
            if "tool_call_parameters" in expectations:
                data["tool_call_parameters"] = expectations["tool_call_parameters"]
            # Allow dynamic_variables to be passed directly in expectations
            if "dynamic_variables" in expectations:
                data["dynamic_variables"] = expectations["dynamic_variables"]
        
        result = await client._request(
            "POST",
            "/convai/agent-testing/create",
            json_data=data
        )
        
        return format_success(
            f"Created test scenario '{name}'",
            {"test": result, "test_id": result.get("id")}
        )
        
    except Exception as e:
        logger.error(f"Failed to create test: {e}")
        error_msg = str(e)
        
        # Provide specific suggestions based on error
        if "422" in error_msg:
            if "chat_history" in error_msg:
                suggestion = "Check that scenarios contain valid conversation messages"
            elif "success_condition" in error_msg:
                suggestion = "Ensure success_condition is a clear evaluation prompt"
            elif "examples" in error_msg:
                suggestion = "Check that success/failure examples have valid response and type fields"
            else:
                suggestion = "Check that all required fields are provided with correct data types"
        else:
            suggestion = "Check API key and agent_id validity"
            
        return format_error(error_msg, suggestion)


async def update_test(
    client,
    test_id: str,
    name: Optional[str] = None,
    scenarios: Optional[List[Dict]] = None,
    expectations: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Update existing test scenario configuration.
    
    Args:
        test_id: Test to update (format: test_XXXX)
        name: New test name (optional)
        scenarios: Updated test flows (optional)
        expectations: Updated expected outcomes (optional)
    
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
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
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


async def delete_test(
    client,
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
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
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


async def get_test_summaries(
    client,
    test_ids: List[str]
) -> Dict[str, Any]:
    """
    Get batch test summaries.
    
    Args:
        test_ids: List of test IDs
    
    Returns:
        Summary statistics for tests
    """
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
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