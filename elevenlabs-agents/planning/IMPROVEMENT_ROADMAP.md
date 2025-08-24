# ElevenLabs Agents MCP Server - Improvement Roadmap

## Overview
This document outlines planned improvements for the elevenlabs-agents MCP server, focusing on simple, useful, and helpful additions without over-engineering.

## Core Principles
- Keep it simple and practical
- Focus on time-saving features
- Maintain clean, modular code structure
- Prioritize user needs (individuals and SMEs)

## 1. New Industry-Specific Agent Templates

### 1.1 Education/Training Agent
**Purpose**: Tutoring, course assistance, educational guidance
```json
{
  "education_tutor": {
    "name": "Educational Assistant",
    "system_prompt": "Patient educator who adapts to learning styles",
    "first_message": "Hello! I'm here to help you learn. What subject are you studying?",
    "voice_preset": "calm",
    "temperature": 0.6,
    "specific_features": [
      "Socratic questioning",
      "Step-by-step explanations",
      "Practice problem generation",
      "Progress tracking mentions"
    ]
  }
}
```

### 1.2 Real Estate Agent
**Purpose**: Property inquiries, virtual tours, appointment scheduling
```json
{
  "real_estate_agent": {
    "name": "Property Specialist",
    "system_prompt": "Knowledgeable realtor showcasing properties",
    "first_message": "Welcome! Are you looking to buy, sell, or rent?",
    "voice_preset": "professional",
    "temperature": 0.7,
    "specific_features": [
      "Property feature highlighting",
      "Neighborhood information",
      "Viewing scheduling",
      "Price negotiation guidance"
    ]
  }
}
```

### 1.3 Banking Assistant
**Purpose**: Account inquiries, transaction help, service information
```json
{
  "banking_assistant": {
    "name": "Banking Services Representative",
    "system_prompt": "Secure, compliant banking assistant",
    "first_message": "Welcome to our banking services. How may I assist you?",
    "voice_preset": "authoritative",
    "temperature": 0.5,
    "specific_features": [
      "Security-first responses",
      "Never ask for full credentials",
      "Transaction status checking",
      "Service recommendations"
    ]
  }
}
```

### 1.4 Insurance Advisor
**Purpose**: Claims assistance, policy information, coverage guidance
```json
{
  "insurance_advisor": {
    "name": "Insurance Claims Specialist",
    "system_prompt": "Empathetic insurance guide for claims and coverage",
    "first_message": "I'm here to help with your insurance needs. Are you filing a claim or have questions about coverage?",
    "voice_preset": "empathetic",
    "temperature": 0.6,
    "specific_features": [
      "Claims process guidance",
      "Document checklist provision",
      "Coverage explanation",
      "Deductible calculations"
    ]
  }
}
```

### 1.5 Travel Planner
**Purpose**: Booking assistance, itinerary planning, travel advice
```json
{
  "travel_planner": {
    "name": "Travel Concierge",
    "system_prompt": "Enthusiastic travel expert creating memorable experiences",
    "first_message": "Ready for an adventure? Tell me about your dream trip!",
    "voice_preset": "energetic",
    "temperature": 0.8,
    "specific_features": [
      "Destination recommendations",
      "Budget optimization",
      "Itinerary building",
      "Local tips and customs"
    ]
  }
}
```

## 2. Enhanced Prompt Templates by Business Size

### 2.1 Enterprise Template Modifier
```python
def apply_enterprise_tone(base_prompt):
    modifiers = [
        "Maintain strict compliance with corporate policies",
        "Document all interactions thoroughly",
        "Follow formal escalation procedures",
        "Use professional business language",
        "Reference ticket numbers and case IDs"
    ]
    return f"{base_prompt}\n\nEnterprise requirements:\n" + "\n".join(modifiers)
```

### 2.2 SME Template Modifier
```python
def apply_sme_tone(base_prompt):
    modifiers = [
        "Balance professionalism with approachability",
        "Be resource-conscious in solutions",
        "Offer practical, implementable advice",
        "Acknowledge budget considerations",
        "Provide self-service options when possible"
    ]
    return f"{base_prompt}\n\nSME approach:\n" + "\n".join(modifiers)
```

### 2.3 Startup Template Modifier
```python
def apply_startup_tone(base_prompt):
    modifiers = [
        "Be innovative and solution-oriented",
        "Use modern, casual language",
        "Emphasize speed and agility",
        "Show enthusiasm for the product",
        "Be transparent about capabilities"
    ]
    return f"{base_prompt}\n\nStartup style:\n" + "\n".join(modifiers)
```

## 3. Additional Voice Presets

### 3.1 Multilingual Preset
```json
{
  "multilingual": {
    "voice_id": "selected_per_language",
    "stability": 0.7,
    "similarity_boost": 0.8,
    "speed": 0.95,
    "style": 0.1,
    "description": "Clear pronunciation for non-native speakers",
    "special_settings": {
      "pause_between_sentences": true,
      "emphasize_clarity": true
    }
  }
}
```

### 3.2 Emergency Preset
```json
{
  "emergency": {
    "voice_id": "cgSgspJ2msm6clMCkdW9",
    "stability": 0.9,
    "similarity_boost": 0.95,
    "speed": 1.0,
    "style": 0.0,
    "description": "Clear, urgent, direct communication",
    "special_settings": {
      "no_small_talk": true,
      "priority_information_first": true
    }
  }
}
```

### 3.3 Training Preset
```json
{
  "training": {
    "voice_id": "EXAVITQu4vr4xnSDxMaL",
    "stability": 0.8,
    "similarity_boost": 0.85,
    "speed": 0.92,
    "style": 0.15,
    "description": "Patient, educational tone for learning",
    "special_settings": {
      "repeat_key_points": true,
      "check_understanding": true
    }
  }
}
```

### 3.4 After-Hours Preset
```json
{
  "after_hours": {
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "stability": 0.6,
    "similarity_boost": 0.75,
    "speed": 0.98,
    "style": 0.1,
    "description": "Acknowledges off-hours, manages expectations",
    "special_settings": {
      "mention_business_hours": true,
      "offer_callback": true
    }
  }
}
```

## 4. New Tool Implementations

### 4.1 Clone Agent Tool
**Purpose**: Duplicate an existing agent with modifications
**API Endpoint Research**: 
- GET `/convai/convai/agents/{agent_id}` to fetch original
- POST `/convai/convai/agents` to create new with modified data

**Implementation Approach**:
```python
async def clone_agent(client, source_agent_id, new_name, modifications=None):
    # 1. Fetch source agent configuration
    source = await client._request("GET", f"/convai/convai/agents/{source_agent_id}")
    
    # 2. Create new agent data
    new_agent_data = {
        "name": new_name,
        "conversation_config": source["conversation_config"],
        "platform_settings": source["platform_settings"]
    }
    
    # 3. Apply modifications if provided
    if modifications:
        # Update specific fields like system_prompt, voice_id, etc.
        pass
    
    # 4. Create new agent
    result = await client._request("POST", "/convai/convai/agents", json_data=new_agent_data)
    return result
```

### 4.2 Bulk Update Agents Tool
**Purpose**: Update multiple agents simultaneously
**API Endpoint Research**:
- GET `/convai/convai/agents` to list agents
- PATCH `/convai/convai/agents/{agent_id}` for each update

**Implementation Approach**:
```python
async def bulk_update_agents(client, agent_ids, updates):
    # Common updates: holiday messages, business hours, escalation contacts
    results = []
    for agent_id in agent_ids:
        try:
            result = await client._request(
                "PATCH", 
                f"/convai/convai/agents/{agent_id}",
                json_data=updates
            )
            results.append({"agent_id": agent_id, "status": "updated"})
        except Exception as e:
            results.append({"agent_id": agent_id, "status": "failed", "error": str(e)})
    return results
```

### 4.3 Agent Backup Tool
**Purpose**: Export agent configuration for backup
**API Endpoint Research**:
- GET `/convai/convai/agents/{agent_id}` for full config
- Include knowledge base attachments
- Include widget settings

**Implementation Approach**:
```python
async def agent_backup(client, agent_id):
    # 1. Get agent configuration
    agent_config = await client._request("GET", f"/convai/convai/agents/{agent_id}")
    
    # 2. Get associated knowledge bases
    # Note: May need to check if endpoint exists for agent-specific knowledge
    
    # 3. Get widget configuration if exists
    
    # 4. Create backup object
    backup = {
        "version": "1.0",
        "timestamp": datetime.now().isoformat(),
        "agent": agent_config,
        "knowledge_bases": [],  # Populated from step 2
        "widgets": []  # Populated from step 3
    }
    
    # 5. Save to file or return as JSON
    return backup
```

### 4.4 Agent Restore Tool
**Purpose**: Restore agent from backup
**API Endpoint Research**:
- POST `/convai/convai/agents` to create new agent
- POST knowledge base attachments if needed

**Implementation Approach**:
```python
async def agent_restore(client, backup_data, new_name=None):
    # 1. Validate backup format
    if backup_data.get("version") != "1.0":
        raise ValueError("Unsupported backup version")
    
    # 2. Prepare agent data
    agent_data = backup_data["agent"]
    if new_name:
        agent_data["name"] = new_name
    
    # 3. Create agent
    new_agent = await client._request("POST", "/convai/convai/agents", json_data=agent_data)
    
    # 4. Restore knowledge bases
    # 5. Restore widget settings
    
    return new_agent
```

### 4.5 Get Agent Metrics Tool
**Purpose**: Simple usage statistics
**API Endpoint Research**:
- Likely need: GET `/convai/convai/agents/{agent_id}/metrics`
- Or analyze conversations: GET `/convai/conversations?agent_id={agent_id}`

**Implementation Approach**:
```python
async def get_agent_metrics(client, agent_id, days=7):
    # Fetch conversations for the agent
    conversations = await client._request(
        "GET",
        "/convai/conversations",
        params={"agent_id": agent_id, "limit": 100}
    )
    
    # Calculate metrics
    metrics = {
        "total_conversations": len(conversations),
        "avg_duration_seconds": 0,
        "success_rate": 0,
        "peak_hours": [],
        "common_topics": [],
        "escalation_rate": 0
    }
    
    # Process conversation data
    # ... calculation logic
    
    return metrics
```

### 4.6 Set Business Hours Tool
**Purpose**: Configure agent availability
**API Endpoint Research**:
- PATCH `/convai/convai/agents/{agent_id}` with schedule in platform_settings

**Implementation Approach**:
```python
async def set_business_hours(client, agent_id, schedule):
    # Schedule format:
    # {
    #   "monday": {"start": "09:00", "end": "17:00"},
    #   "tuesday": {"start": "09:00", "end": "17:00"},
    #   ...
    #   "timezone": "America/New_York"
    # }
    
    update_data = {
        "platform_settings": {
            "widget": {
                "business_hours": schedule,
                "offline_message": "We're currently closed. Our hours are..."
            }
        }
    }
    
    result = await client._request(
        "PATCH",
        f"/convai/convai/agents/{agent_id}",
        json_data=update_data
    )
    return result
```

### 4.7 Add Fallback Responses Tool
**Purpose**: Set default responses for common scenarios
**API Endpoint Research**:
- Likely part of conversation_config in agent settings

**Implementation Approach**:
```python
async def add_fallback_responses(client, agent_id, fallbacks):
    # Fallback scenarios:
    # - no_input: "I didn't hear you, could you repeat?"
    # - unclear_intent: "I'm not sure I understand. Could you rephrase?"
    # - technical_error: "I'm experiencing technical issues. Please try again."
    # - off_topic: "That's outside my area of expertise. Let me connect you with someone who can help."
    
    update_data = {
        "conversation_config": {
            "tts": {
                "fallback_responses": fallbacks
            }
        }
    }
    
    result = await client._request(
        "PATCH",
        f"/convai/convai/agents/{agent_id}",
        json_data=update_data
    )
    return result
```

## 5. New Resource Files

### 5.1 industry_keywords.json
```json
{
  "healthcare": {
    "terms": ["patient", "appointment", "prescription", "symptoms", "doctor"],
    "compliance": ["HIPAA", "privacy", "confidential"],
    "tone": "empathetic and professional"
  },
  "finance": {
    "terms": ["account", "balance", "transaction", "investment", "portfolio"],
    "compliance": ["SEC", "FDIC", "KYC", "AML"],
    "tone": "trustworthy and precise"
  },
  "retail": {
    "terms": ["order", "shipping", "return", "product", "cart"],
    "compliance": ["PCI", "GDPR"],
    "tone": "friendly and helpful"
  }
}
```

### 5.2 escalation_templates.json
```json
{
  "technical_escalation": {
    "trigger_keywords": ["bug", "error", "broken", "not working"],
    "message": "I'll connect you with our technical team who can help resolve this issue.",
    "transfer_to": "technical_support_agent"
  },
  "billing_escalation": {
    "trigger_keywords": ["refund", "charge", "invoice", "payment"],
    "message": "Let me transfer you to our billing specialist for assistance.",
    "transfer_to": "billing_agent"
  },
  "manager_escalation": {
    "trigger_keywords": ["manager", "supervisor", "complaint", "escalate"],
    "message": "I understand your concern. Let me connect you with a supervisor.",
    "transfer_to": "supervisor_agent"
  }
}
```

### 5.3 greeting_variations.json
```json
{
  "time_based": {
    "morning": ["Good morning!", "Morning! How can I help?"],
    "afternoon": ["Good afternoon!", "Hello there!"],
    "evening": ["Good evening!", "Hi, how can I assist you tonight?"]
  },
  "context_based": {
    "returning_customer": ["Welcome back!", "Great to see you again!"],
    "first_time": ["Welcome! I'm here to help.", "Hello! Let me assist you."],
    "after_hours": ["Thanks for reaching out after hours.", "I'm here to help, even outside business hours."]
  },
  "holiday": {
    "christmas": ["Happy holidays!", "Season's greetings!"],
    "new_year": ["Happy New Year!", "Wishing you a great year ahead!"]
  }
}
```

### 5.4 common_objections.json
```json
{
  "price_objections": {
    "too_expensive": {
      "response": "I understand price is important. Let me show you the value you're getting...",
      "follow_up": "We also have flexible payment options available."
    },
    "need_to_think": {
      "response": "Of course! Taking time to decide is important. What specific concerns can I address?",
      "follow_up": "Would you like me to send you more information to review?"
    }
  },
  "trust_objections": {
    "never_heard_of_you": {
      "response": "That's fair! We've been in business for X years and have helped thousands of customers...",
      "follow_up": "I can share some customer success stories if you'd like."
    }
  }
}
```

## 6. Utility Functions

### 6.1 Estimate Monthly Cost
```python
async def estimate_monthly_cost(client, agent_id, usage_profile):
    # Usage profile: conversations_per_day, avg_duration_minutes
    # ElevenLabs pricing (approximate):
    # - Conversational AI: $0.50 per hour
    # - Character generation: included
    
    daily_minutes = usage_profile["conversations_per_day"] * usage_profile["avg_duration_minutes"]
    monthly_hours = (daily_minutes * 30) / 60
    
    estimated_cost = {
        "conversational_hours": monthly_hours,
        "estimated_cost_usd": monthly_hours * 0.50,
        "cost_breakdown": {
            "voice_synthesis": monthly_hours * 0.30,
            "llm_processing": monthly_hours * 0.20
        }
    }
    return estimated_cost
```

### 6.2 Agent Health Check
```python
async def agent_health_check(client, agent_id):
    # Check configuration completeness and common issues
    
    agent = await client._request("GET", f"/convai/convai/agents/{agent_id}")
    
    health_status = {
        "agent_id": agent_id,
        "status": "healthy",
        "issues": [],
        "warnings": [],
        "suggestions": []
    }
    
    # Check system prompt
    if len(agent["conversation_config"]["tts"]["agent_prompt"]) < 50:
        health_status["warnings"].append("System prompt is very short")
        health_status["suggestions"].append("Add more detail to system prompt for better responses")
    
    # Check if knowledge base attached
    # Check if voice is configured
    # Check if first message exists
    # Check temperature settings
    
    return health_status
```

### 6.3 Suggest Improvements
```python
async def suggest_improvements(client, agent_id):
    # Analyze agent performance and suggest optimizations
    
    # Get recent conversations
    conversations = await client._request(
        "GET",
        "/convai/conversations",
        params={"agent_id": agent_id, "limit": 50}
    )
    
    suggestions = {
        "performance": [],
        "configuration": [],
        "content": []
    }
    
    # Analyze patterns
    # - Short conversations might indicate confusion
    # - Long conversations might indicate inefficiency
    # - Repeated questions might indicate unclear responses
    
    return suggestions
```

## 7. Documentation Improvements

### 7.1 QUICK_START.md Structure
```markdown
# 5-Minute Quick Start

## Most Common Use Case: Customer Support Bot
1. Create agent: `create_agent("Support Bot", template="customer_support_pro")`
2. Test it: `simulate_conversation(agent_id, "I need help with my order")`
3. Deploy widget: `get_widget_link(agent_id)`

## Quick Templates
- Sales: `create_agent_from_template("sales_qualifier")`
- Booking: `create_agent_from_template("appointment_scheduler")`
- Support: `create_agent_from_template("customer_support_pro")`
```

### 7.2 TROUBLESHOOTING.md Structure
```markdown
# Common Issues and Solutions

## Agent Not Responding
- Check: Agent is active
- Check: Voice is configured
- Fix: `agent_health_check(agent_id)`

## Poor Response Quality
- Check: System prompt length
- Check: Temperature settings
- Fix: `suggest_improvements(agent_id)`
```

## Implementation Timeline

### Phase 1 (Week 1-2)
- [ ] Clone agent tool
- [ ] Agent health check tool
- [ ] Quick start documentation
- [ ] 3 new agent templates

### Phase 2 (Week 3-4)
- [ ] Bulk update tool
- [ ] Backup/restore tools
- [ ] Industry keywords resource
- [ ] 2 more agent templates

### Phase 3 (Week 5-6)
- [ ] Metrics tool
- [ ] Business hours tool
- [ ] Fallback responses
- [ ] All documentation updates

## Success Metrics
- Tool usage frequency
- Time saved per operation
- Error reduction
- User satisfaction

## Notes
- All implementations should follow existing patterns
- Maintain backward compatibility
- Keep error messages helpful
- Document all new features