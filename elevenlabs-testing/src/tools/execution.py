"""
Test Execution Tools
====================
Tools for running tests and retrieving results.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


async def run_tests_on_agent(
    client,
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
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
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


async def get_test_invocation(
    client,
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
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
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


async def resubmit_test(
    client,
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
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
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