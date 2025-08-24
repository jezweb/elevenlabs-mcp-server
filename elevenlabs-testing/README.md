# ElevenLabs Testing MCP Server

Comprehensive testing and simulation framework for ElevenLabs conversational AI agents.

## Features

- **Test Management**: Create and manage test scenarios with conversation flows
- **Test Execution**: Run test suites with parallel execution support
- **Simulation**: Simulate conversations without production impact
- **Streaming**: Real-time conversation simulation
- **Retry Logic**: Automatically retry failed tests
- **Batch Operations**: Process multiple tests efficiently

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`
2. Add your ElevenLabs API key:
   ```
   ELEVENLABS_API_KEY=your_api_key_here
   ```

## Usage

### Run the server

```bash
python src/server.py
```

### Test the server

```bash
python src/server.py --test
```

## Available Tools

### Test Management

- `list_tests`: Browse test scenarios
- `get_test`: Get test configuration details
- `create_test`: Create new test scenario
- `update_test`: Modify test configuration
- `delete_test`: Remove test scenario
- `get_test_summaries`: Get batch test statistics

### Test Execution

- `run_tests_on_agent`: Execute test suite on an agent
- `get_test_invocation`: Retrieve test execution results
- `resubmit_test`: Retry failed test execution

### Simulation

- `simulate_conversation`: Run conversation simulation
- `stream_simulate_conversation`: Stream real-time simulation

## Examples

### Create a Test Scenario

```python
await create_test(
    name="Customer Support Test",
    agent_id="agent_xyz789",
    test_type="conversation",
    scenarios=[
        {
            "user": "I need help with my order",
            "expected_response": "greeting and offer to help"
        },
        {
            "user": "Order #12345 hasn't arrived",
            "expected_response": "apology and tracking information"
        }
    ],
    expectations={
        "response_time": "<2s",
        "sentiment": "positive",
        "accuracy": ">90%"
    }
)
```

### Run Test Suite

```python
await run_tests_on_agent(
    agent_id="agent_xyz789",
    test_ids=["test_abc123", "test_def456"],
    parallel=True
)
```

### Simulate Conversation

```python
await simulate_conversation(
    agent_id="agent_xyz789",
    user_message="Hello, I have a question about pricing",
    max_turns=10,
    context={
        "user_type": "prospect",
        "product": "enterprise"
    }
)
```

## Test Types

### Conversation Tests
Validate agent responses to specific user inputs and conversation flows.

### Tool Tests
Verify that agents correctly use tools and integrations.

### Integration Tests
Test end-to-end workflows with external systems and MCP servers.

## Environment Variables

- `ELEVENLABS_API_KEY`: Your ElevenLabs API key (required)
- `LOG_LEVEL`: Logging level (default: INFO)
- `API_TIMEOUT`: API request timeout in seconds (default: 30)
- `CACHE_TTL`: Cache time-to-live in seconds (default: 300)
- `MAX_RETRIES`: Maximum retry attempts for API calls (default: 3)

## Error Handling

All tools return consistent error responses with helpful suggestions:

```json
{
  "success": false,
  "error": "Invalid agent ID format",
  "suggestion": "Use format: agent_XXXX"
}
```

## License

MIT