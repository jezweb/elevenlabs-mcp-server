"""
Template and helper tools for ElevenLabs agents.
"""

import logging
from typing import Dict, Any, Optional
from shared import format_success, format_error

logger = logging.getLogger(__name__)


async def get_prompt_template(templates: dict, use_case: str) -> Dict[str, Any]:
    """
    Get a prompt template for a specific use case.
    
    Args:
        templates: Dictionary of prompt templates
        use_case: Type of agent (customer_support, sales, etc.)
    
    Returns:
        Template with system prompt and first message
    """
    if not templates:
        return format_error("No templates available")
    
    template = templates.get(use_case)
    if not template:
        return format_error(
            f"Template '{use_case}' not found",
            f"Available templates: {', '.join(templates.keys())}"
        )
    
    return format_success(
        f"Template for {use_case}",
        {"template": template}
    )


async def get_voice_preset(presets: dict, preset_name: str) -> Dict[str, Any]:
    """
    Get voice configuration preset.
    
    Args:
        presets: Dictionary of voice presets
        preset_name: Name of the preset
    
    Returns:
        Voice preset configuration
    """
    if not presets:
        return format_error("No presets available")
    
    preset = presets.get(preset_name)
    if not preset:
        return format_error(
            f"Preset '{preset_name}' not found",
            f"Available presets: {', '.join(presets.keys())}"
        )
    
    return format_success(
        f"Voice preset: {preset_name}",
        {"preset": preset}
    )


async def create_agent_from_template(
    client,
    templates: dict,
    template_name: str,
    agent_name: str,
    customizations: Optional[dict] = None
) -> Dict[str, Any]:
    """
    Create agent using a template.
    
    Args:
        client: ElevenLabs API client
        templates: Dictionary of agent templates
        template_name: Template to use
        agent_name: Name for the new agent
        customizations: Optional customizations
    
    Returns:
        Created agent details
    """
    if not templates:
        return format_error("No templates available")
    
    template = templates.get(template_name)
    if not template:
        return format_error(
            f"Template '{template_name}' not found",
            f"Available templates: {', '.join(templates.keys())}"
        )
    
    if not agent_name:
        return format_error("Agent name is required")
    
    try:
        # Start with template configuration
        config = template.get("config", {}).copy()
        
        # Apply customizations if provided
        if customizations:
            if "system_prompt" in customizations:
                config["agent"]["prompt"]["prompt"] = customizations["system_prompt"]
            if "first_message" in customizations:
                config["agent"]["prompt"]["first_message"] = customizations["first_message"]
            if "voice_id" in customizations:
                config["tts"]["voice_id"] = customizations["voice_id"]
        
        # Create agent with template config
        agent_data = {
            "conversation_config": config,
            "name": agent_name
        }
        
        result = await client.create_agent(agent_data)
        
        return format_success(
            f"Agent '{agent_name}' created from template '{template_name}'",
            {
                "agent_id": result.get("agent_id"),
                "name": agent_name,
                "template": template_name,
                "config": config
            }
        )
    except Exception as e:
        logger.error(f"Failed to create agent from template: {e}")
        return format_error(str(e))


async def suggest_voice_for_use_case(presets: dict, use_case: str) -> Dict[str, Any]:
    """
    Suggest voices for a specific use case.
    
    Args:
        presets: Dictionary of voice presets
        use_case: Business use case
    
    Returns:
        Recommended voices with explanations
    """
    if not presets:
        return format_error("No voice presets available")
    
    # Find voices matching the use case
    recommendations = []
    for name, preset in presets.items():
        use_cases = preset.get("use_cases", [])
        if use_case.lower() in [uc.lower() for uc in use_cases]:
            recommendations.append({
                "name": name,
                "voice_id": preset.get("voice_id"),
                "description": preset.get("description"),
                "personality": preset.get("personality"),
                "reason": f"Recommended for {use_case}"
            })
    
    if not recommendations:
        # Provide general recommendations
        recommendations = [
            {
                "name": "professional",
                "voice_id": presets.get("professional", {}).get("voice_id"),
                "description": "Clear, professional voice",
                "reason": "General purpose, works for most use cases"
            }
        ]
    
    return format_success(
        f"Voice recommendations for {use_case}",
        {
            "use_case": use_case,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
    )


async def validate_prompt(prompt: str, min_length: int = 10, max_length: int = 2000) -> Dict[str, Any]:
    """
    Validate a system prompt.
    
    Args:
        prompt: Prompt to validate
        min_length: Minimum length
        max_length: Maximum length
    
    Returns:
        Validation result with suggestions
    """
    if not prompt:
        return format_error("Prompt is required")
    
    issues = []
    suggestions = []
    
    # Check length
    if len(prompt) < min_length:
        issues.append(f"Prompt too short ({len(prompt)} chars, min {min_length})")
        suggestions.append("Provide more detailed instructions")
    elif len(prompt) > max_length:
        issues.append(f"Prompt too long ({len(prompt)} chars, max {max_length})")
        suggestions.append("Condense instructions to essential points")
    
    # Check for common best practices
    if "you are" not in prompt.lower():
        suggestions.append("Consider starting with 'You are...' to define the agent's role")
    
    if not any(word in prompt.lower() for word in ["help", "assist", "support", "provide"]):
        suggestions.append("Consider specifying what the agent should help with")
    
    if len(issues) > 0:
        return format_error(
            "Prompt validation failed",
            {"issues": issues, "suggestions": suggestions}
        )
    
    return format_success(
        "Prompt is valid",
        {
            "length": len(prompt),
            "suggestions": suggestions if suggestions else ["Prompt follows best practices"]
        }
    )


async def get_agent_template(templates: dict, template_name: str) -> Dict[str, Any]:
    """
    Get a complete agent template.
    
    Args:
        templates: Dictionary of agent templates
        template_name: Name of the template
    
    Returns:
        Complete template configuration
    """
    if not templates:
        return format_error("No templates available")
    
    template = templates.get(template_name)
    if not template:
        return format_error(
            f"Template '{template_name}' not found",
            f"Available templates: {', '.join(templates.keys())}"
        )
    
    return format_success(
        f"Agent template: {template_name}",
        {"template": template}
    )


async def list_agent_templates(templates: dict) -> Dict[str, Any]:
    """
    List all available agent templates.
    
    Args:
        templates: Dictionary of agent templates
    
    Returns:
        List of templates with descriptions
    """
    if not templates:
        return format_error("No templates available")
    
    template_list = []
    for name, template in templates.items():
        template_list.append({
            "name": name,
            "description": template.get("description", ""),
            "use_cases": template.get("use_cases", []),
            "industry": template.get("industry", "general")
        })
    
    return format_success(
        f"Found {len(template_list)} templates",
        {
            "count": len(template_list),
            "templates": template_list
        }
    )