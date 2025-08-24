"""
ElevenLabs Agents MCP Server Tools

This module contains all tools for managing ElevenLabs conversational AI agents.
"""

from .agents import (
    create_agent,
    list_agents,
    get_agent,
    update_agent,
    delete_agent,
    update_system_prompt,
    duplicate_agent
)

from .voice import (
    configure_voice,
    set_llm_config,
    list_voices,
    get_shared_voices,
    add_shared_voice
)

from .transfers import (
    add_transfer_to_agent,
    configure_webhook
)

from .templates import (
    get_agent_template,
    list_agent_templates,
    get_prompt_template,
    get_voice_preset,
    create_agent_from_template,
    suggest_voice_for_use_case,
    validate_prompt
)

from .testing import (
    simulate_conversation,
    create_test,
    get_test_results
)

from .widgets import (
    get_widget_link,
    get_agent_link,
    get_widget,
    create_widget_avatar,
    calculate_llm_usage
)

__all__ = [
    # Agent management
    'create_agent',
    'list_agents',
    'get_agent',
    'update_agent',
    'delete_agent',
    'update_system_prompt',
    'duplicate_agent',
    # Voice configuration
    'configure_voice',
    'set_llm_config',
    'list_voices',
    'get_shared_voices',
    'add_shared_voice',
    # Transfers
    'add_transfer_to_agent',
    'configure_webhook',
    # Templates
    'get_agent_template',
    'list_agent_templates',
    'get_prompt_template',
    'get_voice_preset',
    'create_agent_from_template',
    'suggest_voice_for_use_case',
    'validate_prompt',
    # Testing
    'simulate_conversation',
    'create_test',
    'get_test_results',
    # Widgets
    'get_widget_link',
    'get_agent_link',
    'get_widget',
    'create_widget_avatar',
    'calculate_llm_usage'
]