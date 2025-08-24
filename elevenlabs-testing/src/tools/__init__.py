"""
Testing Tools Package
=====================
Tools for testing and simulating ElevenLabs conversational AI agents.
"""

# Test Management
from .tests import (
    list_tests,
    get_test,
    create_test,
    update_test,
    delete_test,
    get_test_summaries
)

# Test Execution
from .execution import (
    run_tests_on_agent,
    get_test_invocation,
    resubmit_test
)

# Simulation
from .simulation import (
    simulate_conversation,
    stream_simulate_conversation
)

__all__ = [
    # Test Management
    'list_tests',
    'get_test',
    'create_test',
    'update_test',
    'delete_test',
    'get_test_summaries',
    # Test Execution
    'run_tests_on_agent',
    'get_test_invocation',
    'resubmit_test',
    # Simulation
    'simulate_conversation',
    'stream_simulate_conversation'
]