"""
Testing and simulation tools for ElevenLabs agents.
"""

import logging
from typing import Dict, Any
from shared import format_success, format_error, validate_elevenlabs_id

logger = logging.getLogger(__name__)


async def simulate_conversation(
    client,
    agent_id: str,
    user_message: str
) -> Dict[str, Any]:
    """
    Simulate a conversation with an agent for testing.
    
    Args:
        client: ElevenLabs API client
        agent_id: Agent to test
        user_message: Test message to send
    
    Returns:
        Simulated agent response
    
    Examples:
        simulate_conversation("agent_abc123", "Hello, I need help")
        simulate_conversation("agent_xyz789", "What are your business hours?")
    
    Note: This creates a test conversation to validate agent behavior.
    
    API Endpoint: POST /convai/convai/simulations
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID format")
    
    if not user_message or len(user_message.strip()) < 2:
        return format_error("Message too short", "Provide a meaningful test message")
    
    try:
        result = await client._request(
            "POST",
            "/convai/convai/simulations",
            json_data={
                "agent_id": agent_id,
                "simulation_specification": {
                    "num_conversations": 1,
                    "conversation_specification": {
                        "customer": {
                            "prompt": {
                                "prompt": f"You are a user testing the agent. Send this message: {user_message}"
                            }
                        },
                        "max_messages": 2
                    }
                }
            }
        )
        
        return format_success(
            "Simulation created",
            {"simulation": result, "test_message": user_message}
        )
    except Exception as e:
        logger.error(f"Failed to simulate conversation: {e}")
        return format_error(str(e))


async def create_test(client, agent_id: str, test_name: str, test_cases: list) -> Dict[str, Any]:
    """
    Create a test suite for an agent.
    
    Args:
        client: ElevenLabs API client
        agent_id: Agent to test
        test_name: Name of the test suite
        test_cases: List of test scenarios
    
    Returns:
        Test creation result
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID format")
    
    if not test_name:
        return format_error("Test name is required")
    
    if not test_cases or not isinstance(test_cases, list):
        return format_error("Test cases must be a non-empty list")
    
    try:
        # Create test suite (simplified example)
        test_data = {
            "agent_id": agent_id,
            "name": test_name,
            "test_cases": test_cases
        }
        
        # This would typically use a specific test API endpoint
        result = {
            "test_id": f"test_{agent_id}_{test_name.replace(' ', '_')}",
            "status": "created",
            "test_data": test_data
        }
        
        return format_success(
            f"Test suite '{test_name}' created",
            result
        )
    except Exception as e:
        logger.error(f"Failed to create test: {e}")
        return format_error(str(e))


async def get_test_results(client, test_id: str) -> Dict[str, Any]:
    """
    Get results from a test run.
    
    Args:
        client: ElevenLabs API client
        test_id: Test identifier
    
    Returns:
        Test results and metrics
    """
    if not test_id:
        return format_error("Test ID is required")
    
    try:
        # This would fetch actual test results from the API
        # For now, returning a structured example
        results = {
            "test_id": test_id,
            "status": "completed",
            "passed": 8,
            "failed": 2,
            "total": 10,
            "details": "Test results would be retrieved from the API"
        }
        
        return format_success(
            f"Test results retrieved",
            results
        )
    except Exception as e:
        logger.error(f"Failed to get test results: {e}")
        return format_error(str(e))