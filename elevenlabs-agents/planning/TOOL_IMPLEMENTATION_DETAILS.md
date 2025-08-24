# Tool Implementation Details

## 1. Clone Agent Tool

### Purpose
Quickly duplicate an existing agent with modifications, saving time on complex configurations.

### Implementation Steps
```python
# File: src/tools/agents.py (addition)

async def clone_agent(
    client,
    source_agent_id: str,
    new_name: str,
    modifications: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Clone an existing agent with optional modifications.
    
    Args:
        source_agent_id: Agent to clone from
        new_name: Name for the new agent
        modifications: Optional dict with fields to override
            - system_prompt: New system prompt
            - first_message: New greeting
            - voice_id: Different voice
            - temperature: Different temperature
            - language: Different language
    
    Returns:
        New agent details with agent_id
    """
    # Step 1: Validate source agent exists
    if not validate_elevenlabs_id(source_agent_id, 'agent'):
        return format_error("Invalid source agent ID")
    
    # Step 2: Fetch source configuration
    try:
        source = await client._request(
            "GET",
            f"/convai/convai/agents/{source_agent_id}",
            use_cache=True
        )
    except Exception as e:
        return format_error(f"Failed to fetch source agent: {e}")
    
    # Step 3: Prepare new agent data
    new_agent_data = {
        "name": new_name,
        "conversation_config": source.get("conversation_config", {}),
        "platform_settings": source.get("platform_settings", {})
    }
    
    # Step 4: Apply modifications
    if modifications:
        if "system_prompt" in modifications:
            new_agent_data["conversation_config"]["agent"]["prompt"]["prompt"] = modifications["system_prompt"]
        if "first_message" in modifications:
            new_agent_data["conversation_config"]["agent"]["first_message"] = modifications["first_message"]
        if "voice_id" in modifications:
            new_agent_data["conversation_config"]["tts"]["voice_id"] = modifications["voice_id"]
        if "temperature" in modifications:
            new_agent_data["conversation_config"]["llm"]["temperature"] = float(modifications["temperature"])
        if "language" in modifications:
            new_agent_data["conversation_config"]["agent"]["language"] = modifications["language"]
    
    # Step 5: Create new agent
    try:
        result = await client._request(
            "POST",
            "/convai/convai/agents",
            json_data=new_agent_data
        )
        return format_success(
            f"Cloned agent from {source_agent_id}",
            {"agent": result, "source_id": source_agent_id}
        )
    except Exception as e:
        return format_error(f"Failed to create cloned agent: {e}")
```

### Server Registration
```python
# In src/server.py
@mcp.tool()
async def clone_agent_tool(
    source_agent_id: str,
    new_name: str,
    system_prompt: Optional[str] = None,
    first_message: Optional[str] = None,
    voice_id: Optional[str] = None,
    temperature: Optional[str] = None,
    language: Optional[str] = None
) -> Dict[str, Any]:
    """Clone an existing agent with optional modifications."""
    modifications = {}
    if system_prompt:
        modifications["system_prompt"] = system_prompt
    if first_message:
        modifications["first_message"] = first_message
    if voice_id:
        modifications["voice_id"] = voice_id
    if temperature:
        modifications["temperature"] = temperature
    if language:
        modifications["language"] = language
    
    return await clone_agent(client, source_agent_id, new_name, modifications)
```

## 2. Bulk Update Agents Tool

### Purpose
Update multiple agents simultaneously for common changes like holiday messages or business hours.

### Implementation
```python
# File: src/tools/agents.py (addition)

async def bulk_update_agents(
    client,
    agent_ids: List[str],
    update_type: str,
    update_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update multiple agents with the same changes.
    
    Args:
        agent_ids: List of agent IDs to update
        update_type: Type of update ('message', 'hours', 'voice', 'prompt')
        update_data: Update configuration based on type
    
    Update Types:
        - message: Update first_message or add announcement
        - hours: Update business hours
        - voice: Change voice settings
        - prompt: Append to system prompt
    """
    # Validate all agent IDs
    for agent_id in agent_ids:
        if not validate_elevenlabs_id(agent_id, 'agent'):
            return format_error(f"Invalid agent ID: {agent_id}")
    
    # Prepare update payload based on type
    update_payload = {}
    
    if update_type == "message":
        # Holiday message, announcement, etc.
        update_payload = {
            "conversation_config": {
                "agent": {
                    "first_message": update_data.get("first_message")
                }
            }
        }
    elif update_type == "hours":
        # Business hours update
        update_payload = {
            "platform_settings": {
                "widget": {
                    "business_hours": update_data.get("schedule"),
                    "offline_message": update_data.get("offline_message")
                }
            }
        }
    elif update_type == "voice":
        # Voice settings update
        update_payload = {
            "conversation_config": {
                "tts": {
                    "voice_settings": update_data.get("voice_settings")
                }
            }
        }
    elif update_type == "prompt":
        # Append to prompt (for temporary notices)
        append_text = update_data.get("append_text", "")
        # Need to fetch current prompt first for each agent
        pass  # More complex implementation
    
    # Execute updates
    results = []
    success_count = 0
    
    for agent_id in agent_ids:
        try:
            await client._request(
                "PATCH",
                f"/convai/convai/agents/{agent_id}",
                json_data=update_payload
            )
            results.append({"agent_id": agent_id, "status": "success"})
            success_count += 1
        except Exception as e:
            results.append({
                "agent_id": agent_id,
                "status": "failed",
                "error": str(e)
            })
    
    return format_success(
        f"Updated {success_count}/{len(agent_ids)} agents",
        {"results": results, "update_type": update_type}
    )
```

## 3. Agent Health Check Tool

### Purpose
Verify agent configuration and identify potential issues.

### Implementation
```python
# File: src/tools/testing.py (addition)

async def agent_health_check(
    client,
    agent_id: str
) -> Dict[str, Any]:
    """
    Comprehensive health check for an agent.
    
    Checks:
        - Configuration completeness
        - System prompt quality
        - Voice configuration
        - Knowledge base attachment
        - Recent performance
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID")
    
    health_report = {
        "agent_id": agent_id,
        "status": "healthy",
        "score": 100,
        "issues": [],
        "warnings": [],
        "suggestions": []
    }
    
    try:
        # Fetch agent configuration
        agent = await client._request(
            "GET",
            f"/convai/convai/agents/{agent_id}",
            use_cache=True
        )
        
        # Check 1: System prompt
        prompt = agent.get("conversation_config", {}).get("agent", {}).get("prompt", {}).get("prompt", "")
        if len(prompt) < 50:
            health_report["warnings"].append("System prompt is too short (< 50 chars)")
            health_report["suggestions"].append("Add more detail to improve response quality")
            health_report["score"] -= 10
        elif len(prompt) < 100:
            health_report["warnings"].append("System prompt could be more detailed")
            health_report["score"] -= 5
        
        # Check 2: First message
        first_msg = agent.get("conversation_config", {}).get("agent", {}).get("first_message", "")
        if not first_msg:
            health_report["issues"].append("No first message configured")
            health_report["score"] -= 15
        elif len(first_msg) < 10:
            health_report["warnings"].append("First message is very short")
            health_report["score"] -= 5
        
        # Check 3: Voice configuration
        voice_id = agent.get("conversation_config", {}).get("tts", {}).get("voice_id")
        if not voice_id:
            health_report["issues"].append("No voice configured")
            health_report["score"] -= 20
        
        voice_settings = agent.get("conversation_config", {}).get("tts", {}).get("voice_settings", {})
        if not voice_settings:
            health_report["warnings"].append("Using default voice settings")
            health_report["suggestions"].append("Configure voice settings for better quality")
            health_report["score"] -= 5
        
        # Check 4: LLM configuration
        temperature = agent.get("conversation_config", {}).get("llm", {}).get("temperature", 0.7)
        if temperature > 0.9:
            health_report["warnings"].append("High temperature may cause inconsistent responses")
            health_report["suggestions"].append("Consider lowering temperature for more consistent behavior")
        elif temperature < 0.3:
            health_report["warnings"].append("Low temperature may make responses too rigid")
            health_report["suggestions"].append("Consider raising temperature for more natural conversation")
        
        # Check 5: Knowledge base (check if endpoint exists)
        try:
            kb_response = await client._request(
                "GET",
                "/convai/knowledge_base",
                params={"agent_id": agent_id},
                use_cache=True
            )
            kb_count = len(kb_response.get("documents", []))
            if kb_count == 0:
                health_report["suggestions"].append("No knowledge base attached - consider adding documents")
            else:
                health_report["suggestions"].append(f"Knowledge base has {kb_count} documents")
        except:
            pass  # Knowledge base check is optional
        
        # Check 6: Recent conversations (performance check)
        try:
            conversations = await client._request(
                "GET",
                "/convai/conversations",
                params={"agent_id": agent_id, "limit": 10},
                use_cache=True
            )
            
            if len(conversations) == 0:
                health_report["warnings"].append("No recent conversations - agent may not be tested")
                health_report["suggestions"].append("Run test conversations to verify functionality")
            else:
                # Could analyze conversation quality here
                pass
        except:
            pass  # Conversation check is optional
        
        # Determine overall status
        if health_report["score"] >= 90:
            health_report["status"] = "excellent"
        elif health_report["score"] >= 75:
            health_report["status"] = "good"
        elif health_report["score"] >= 60:
            health_report["status"] = "fair"
        else:
            health_report["status"] = "needs_attention"
        
        return format_success(
            f"Health check complete: {health_report['status']}",
            health_report
        )
        
    except Exception as e:
        return format_error(f"Health check failed: {e}")
```

## 4. Agent Backup & Restore Tools

### Backup Implementation
```python
# File: src/tools/agents.py (addition)

async def backup_agent(
    client,
    agent_id: str,
    include_knowledge: bool = True
) -> Dict[str, Any]:
    """
    Create a complete backup of an agent configuration.
    
    Args:
        agent_id: Agent to backup
        include_knowledge: Include knowledge base documents
    
    Returns:
        Backup data that can be saved or used for restore
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID")
    
    try:
        # Get agent configuration
        agent_config = await client._request(
            "GET",
            f"/convai/convai/agents/{agent_id}",
            use_cache=False  # Want fresh data for backup
        )
        
        backup = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "agent_id": agent_id,
            "agent_name": agent_config.get("name"),
            "agent_config": agent_config,
            "knowledge_bases": [],
            "metadata": {
                "include_knowledge": include_knowledge
            }
        }
        
        # Get knowledge base if requested
        if include_knowledge:
            try:
                kb_response = await client._request(
                    "GET",
                    "/convai/knowledge_base",
                    params={"agent_id": agent_id},
                    use_cache=False
                )
                backup["knowledge_bases"] = kb_response.get("documents", [])
            except:
                backup["metadata"]["knowledge_fetch_failed"] = True
        
        return format_success(
            f"Agent backup created",
            {"backup": backup, "size_bytes": len(json.dumps(backup))}
        )
        
    except Exception as e:
        return format_error(f"Backup failed: {e}")
```

### Restore Implementation
```python
async def restore_agent(
    client,
    backup_data: Dict[str, Any],
    new_name: Optional[str] = None,
    restore_knowledge: bool = True
) -> Dict[str, Any]:
    """
    Restore an agent from backup data.
    
    Args:
        backup_data: Backup created by backup_agent
        new_name: Optional new name (uses original if not provided)
        restore_knowledge: Restore knowledge base documents
    
    Returns:
        Restored agent details
    """
    # Validate backup format
    if backup_data.get("version") != "1.0":
        return format_error(f"Unsupported backup version: {backup_data.get('version')}")
    
    try:
        # Prepare agent configuration
        agent_config = backup_data["agent_config"].copy()
        
        # Update name if provided
        if new_name:
            agent_config["name"] = new_name
        else:
            # Add "Restored" prefix to avoid confusion
            agent_config["name"] = f"Restored - {agent_config.get('name', 'Agent')}"
        
        # Remove read-only fields
        agent_config.pop("agent_id", None)
        agent_config.pop("created_at", None)
        agent_config.pop("updated_at", None)
        
        # Create new agent
        new_agent = await client._request(
            "POST",
            "/convai/convai/agents",
            json_data=agent_config
        )
        
        new_agent_id = new_agent.get("agent_id")
        
        # Restore knowledge base if requested and available
        restored_kb = []
        if restore_knowledge and backup_data.get("knowledge_bases"):
            for doc in backup_data["knowledge_bases"]:
                try:
                    # Create knowledge base document
                    kb_data = {
                        "agent_id": new_agent_id,
                        "name": doc.get("name"),
                        "content": doc.get("content"),
                        "type": doc.get("type", "text")
                    }
                    
                    await client._request(
                        "POST",
                        "/convai/knowledge_base",
                        json_data=kb_data
                    )
                    restored_kb.append(doc.get("name"))
                except Exception as e:
                    logger.warning(f"Failed to restore document {doc.get('name')}: {e}")
        
        return format_success(
            f"Agent restored successfully",
            {
                "agent": new_agent,
                "original_id": backup_data.get("agent_id"),
                "restored_knowledge_bases": restored_kb
            }
        )
        
    except Exception as e:
        return format_error(f"Restore failed: {e}")
```

## 5. Get Agent Metrics Tool

### Implementation
```python
# File: src/tools/testing.py (addition)

async def get_agent_metrics(
    client,
    agent_id: str,
    days: int = 7
) -> Dict[str, Any]:
    """
    Calculate usage metrics for an agent.
    
    Args:
        agent_id: Agent to analyze
        days: Number of days to analyze (1-30)
    
    Returns:
        Metrics including usage, performance, and patterns
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID")
    
    if days < 1 or days > 30:
        return format_error("Days must be between 1 and 30")
    
    try:
        # Fetch conversations
        conversations = await client._request(
            "GET",
            "/convai/conversations",
            params={"agent_id": agent_id, "limit": 100},
            use_cache=True
        )
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Filter conversations by date
        relevant_convos = []
        for convo in conversations:
            convo_date = datetime.fromisoformat(convo.get("started_at", ""))
            if start_date <= convo_date <= end_date:
                relevant_convos.append(convo)
        
        # Calculate metrics
        metrics = {
            "agent_id": agent_id,
            "period_days": days,
            "total_conversations": len(relevant_convos),
            "daily_average": len(relevant_convos) / days if days > 0 else 0,
            "metrics": {}
        }
        
        if relevant_convos:
            # Duration metrics
            durations = []
            for convo in relevant_convos:
                if convo.get("ended_at") and convo.get("started_at"):
                    start = datetime.fromisoformat(convo["started_at"])
                    end = datetime.fromisoformat(convo["ended_at"])
                    duration = (end - start).total_seconds()
                    durations.append(duration)
            
            if durations:
                metrics["metrics"]["avg_duration_seconds"] = sum(durations) / len(durations)
                metrics["metrics"]["min_duration_seconds"] = min(durations)
                metrics["metrics"]["max_duration_seconds"] = max(durations)
                metrics["metrics"]["total_conversation_time_hours"] = sum(durations) / 3600
            
            # Time pattern analysis
            hour_distribution = {}
            day_distribution = {}
            
            for convo in relevant_convos:
                convo_date = datetime.fromisoformat(convo.get("started_at", ""))
                hour = convo_date.hour
                day = convo_date.strftime("%A")
                
                hour_distribution[hour] = hour_distribution.get(hour, 0) + 1
                day_distribution[day] = day_distribution.get(day, 0) + 1
            
            # Find peak hours
            if hour_distribution:
                peak_hour = max(hour_distribution, key=hour_distribution.get)
                metrics["metrics"]["peak_hour"] = f"{peak_hour}:00"
                metrics["metrics"]["hour_distribution"] = hour_distribution
            
            if day_distribution:
                peak_day = max(day_distribution, key=day_distribution.get)
                metrics["metrics"]["peak_day"] = peak_day
                metrics["metrics"]["day_distribution"] = day_distribution
            
            # Estimated costs (rough calculation)
            total_hours = metrics["metrics"].get("total_conversation_time_hours", 0)
            metrics["metrics"]["estimated_cost_usd"] = round(total_hours * 0.50, 2)  # $0.50/hour estimate
        
        return format_success(
            f"Metrics calculated for {days} days",
            metrics
        )
        
    except Exception as e:
        return format_error(f"Failed to calculate metrics: {e}")
```

## 6. Set Business Hours Tool

### Implementation
```python
# File: src/tools/agents.py (addition)

async def set_business_hours(
    client,
    agent_id: str,
    schedule: Dict[str, Any],
    timezone: str = "America/New_York",
    offline_message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Configure business hours for an agent.
    
    Args:
        agent_id: Agent to configure
        schedule: Dict with days and hours
            Example: {
                "monday": {"start": "09:00", "end": "17:00"},
                "tuesday": {"start": "09:00", "end": "17:00"},
                ...
                "sunday": None  # Closed
            }
        timezone: Timezone for the schedule
        offline_message: Message when outside hours
    
    Returns:
        Updated configuration
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID")
    
    # Validate schedule format
    valid_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for day in valid_days:
        if day not in schedule:
            schedule[day] = None  # Default to closed
    
    # Default offline message
    if not offline_message:
        offline_message = "We're currently closed. Our business hours are Monday-Friday 9 AM - 5 PM. Please leave a message and we'll get back to you."
    
    try:
        # Prepare update payload
        update_data = {
            "platform_settings": {
                "widget": {
                    "business_hours": {
                        "enabled": True,
                        "timezone": timezone,
                        "schedule": schedule,
                        "offline_message": offline_message,
                        "show_schedule": True
                    }
                }
            }
        }
        
        # Update agent
        result = await client._request(
            "PATCH",
            f"/convai/convai/agents/{agent_id}",
            json_data=update_data
        )
        
        return format_success(
            "Business hours configured",
            {
                "agent_id": agent_id,
                "schedule": schedule,
                "timezone": timezone
            }
        )
        
    except Exception as e:
        return format_error(f"Failed to set business hours: {e}")
```

## 7. Add Fallback Responses Tool

### Implementation
```python
# File: src/tools/agents.py (addition)

async def add_fallback_responses(
    client,
    agent_id: str,
    fallback_type: str,
    response: str
) -> Dict[str, Any]:
    """
    Add fallback responses for common scenarios.
    
    Args:
        agent_id: Agent to configure
        fallback_type: Type of fallback
            - "no_input": User didn't speak
            - "unclear": Can't understand intent
            - "error": Technical issue
            - "off_topic": Outside scope
            - "profanity": Inappropriate content
            - "long_pause": User inactive
        response: Fallback message
    
    Returns:
        Updated configuration
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID")
    
    valid_types = ["no_input", "unclear", "error", "off_topic", "profanity", "long_pause"]
    if fallback_type not in valid_types:
        return format_error(f"Invalid fallback type. Use one of: {valid_types}")
    
    try:
        # First, get current agent config to preserve existing fallbacks
        agent = await client._request(
            "GET",
            f"/convai/convai/agents/{agent_id}",
            use_cache=False
        )
        
        # Get existing fallbacks or create new structure
        current_config = agent.get("conversation_config", {})
        current_fallbacks = current_config.get("fallback_responses", {})
        
        # Add new fallback
        current_fallbacks[fallback_type] = response
        
        # Update agent
        update_data = {
            "conversation_config": {
                "fallback_responses": current_fallbacks
            }
        }
        
        result = await client._request(
            "PATCH",
            f"/convai/convai/agents/{agent_id}",
            json_data=update_data
        )
        
        return format_success(
            f"Added {fallback_type} fallback response",
            {
                "agent_id": agent_id,
                "fallback_type": fallback_type,
                "response": response,
                "total_fallbacks": len(current_fallbacks)
            }
        )
        
    except Exception as e:
        return format_error(f"Failed to add fallback response: {e}")
```

## 8. Estimate Monthly Cost Tool

### Implementation
```python
# File: src/tools/widgets.py (addition to existing file)

async def estimate_monthly_cost(
    client,
    agent_id: str,
    estimated_conversations_per_day: int,
    estimated_minutes_per_conversation: float
) -> Dict[str, Any]:
    """
    Estimate monthly costs for an agent.
    
    Args:
        agent_id: Agent to estimate costs for
        estimated_conversations_per_day: Expected daily volume
        estimated_minutes_per_conversation: Average conversation length
    
    Returns:
        Cost breakdown and estimates
    
    Pricing Model (approximate):
        - Conversational AI: $0.50 per hour
        - Voice synthesis: Included
        - LLM processing: Included
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID")
    
    # Calculate usage
    daily_minutes = estimated_conversations_per_day * estimated_minutes_per_conversation
    monthly_minutes = daily_minutes * 30  # 30 days per month
    monthly_hours = monthly_minutes / 60
    
    # Cost calculation (based on ElevenLabs pricing)
    cost_per_hour = 0.50  # USD
    monthly_cost = monthly_hours * cost_per_hour
    
    # Create detailed breakdown
    cost_breakdown = {
        "agent_id": agent_id,
        "usage_forecast": {
            "conversations_per_day": estimated_conversations_per_day,
            "minutes_per_conversation": estimated_minutes_per_conversation,
            "daily_minutes": daily_minutes,
            "monthly_minutes": monthly_minutes,
            "monthly_hours": round(monthly_hours, 2)
        },
        "cost_estimate": {
            "monthly_cost_usd": round(monthly_cost, 2),
            "daily_cost_usd": round(monthly_cost / 30, 2),
            "cost_per_conversation_usd": round(monthly_cost / (estimated_conversations_per_day * 30), 3),
            "cost_per_hour_usd": cost_per_hour
        },
        "cost_optimization_tips": []
    }
    
    # Add optimization suggestions
    if estimated_minutes_per_conversation > 10:
        cost_breakdown["cost_optimization_tips"].append(
            "Consider adding more self-service options to reduce conversation length"
        )
    
    if estimated_conversations_per_day > 100:
        cost_breakdown["cost_optimization_tips"].append(
            "High volume detected - consider implementing FAQ bot for common questions"
        )
    
    if monthly_cost > 500:
        cost_breakdown["cost_optimization_tips"].append(
            "Consider enterprise pricing for better rates at this volume"
        )
    
    return format_success(
        f"Estimated monthly cost: ${monthly_cost:.2f}",
        cost_breakdown
    )
```

## Testing Strategy for All Tools

### Unit Tests Structure
```python
# File: tests/test_new_tools.py

import pytest
from unittest.mock import Mock, patch

class TestNewTools:
    
    @pytest.mark.asyncio
    async def test_clone_agent(self):
        # Test successful clone
        # Test with modifications
        # Test invalid source ID
        pass
    
    @pytest.mark.asyncio
    async def test_bulk_update(self):
        # Test message update
        # Test hours update
        # Test partial failures
        pass
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        # Test healthy agent
        # Test agent with issues
        # Test missing components
        pass
    
    @pytest.mark.asyncio
    async def test_backup_restore(self):
        # Test backup creation
        # Test restore from backup
        # Test version mismatch
        pass
```

## Deployment Checklist

- [ ] Add new tool functions to appropriate modules
- [ ] Register tools in server.py
- [ ] Update __init__.py exports
- [ ] Add comprehensive docstrings
- [ ] Implement error handling
- [ ] Add input validation
- [ ] Create unit tests
- [ ] Update documentation
- [ ] Test with real API
- [ ] Monitor for rate limits
- [ ] Add to CHANGELOG.md