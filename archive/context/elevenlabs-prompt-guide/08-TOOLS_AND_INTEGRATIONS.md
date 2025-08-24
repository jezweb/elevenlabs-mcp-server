# Tools and Integrations Guide for ElevenLabs Agents

## Overview

Tools extend your agent's capabilities beyond conversation, enabling actions like transferring calls, collecting data, searching knowledge bases, and triggering webhooks. Proper tool configuration is essential for creating functional, business-ready agents.

## Core Tools Reference

### Essential Tools Overview

| Tool | Purpose | Use Cases | Configuration Complexity |
|------|---------|-----------|-------------------------|
| **End Call** | Gracefully terminate conversation | All agents | Simple |
| **Transfer to Agent** | Hand off to another AI agent | Multi-agent systems | Moderate |
| **Transfer to Number** | Transfer to human/phone | Escalation, emergency | Simple |
| **Knowledge Base** | Search and retrieve information | FAQ, support | Moderate |
| **Data Collection** | Gather structured information | Booking, forms | Complex |
| **Webhook** | Trigger external actions | CRM, automation | Complex |
| **Detect Language** | Identify spoken language | Multi-lingual support | Simple |
| **Skip Turn** | Let customer continue | Active listening | Simple |

---

## Tool Configuration Details

### 1. End Call Tool

**Purpose:** Allow agent to end conversation naturally

```yaml
tool_configuration:
  name: "end_call"
  enabled: true
  
usage_instructions: |
  ## IN ADAPTABILITY SECTION
  End the call when:
  - Customer says goodbye/thanks/that's all
  - Issue is resolved and confirmed
  - Customer requests to end call
  - After successful transfer completion
  
  Before ending:
  - Confirm resolution: "Is there anything else?"
  - Thank customer: "Thank you for calling"
  - Provide reference: "Your reference is {{conversation_id}}"
  
when_not_to_use:
  - During active troubleshooting
  - When customer is speaking
  - In middle of data collection
  - Before confirming resolution
```

### 2. Transfer to AI Agent

**Purpose:** Seamless handoff between specialized agents

```yaml
tool_configuration:
  name: "transfer_to_ai_agent"
  enabled: true
  
targets:
  - agent_id: "agent_abc123xyz"
    name: "Booking Specialist"
    condition: "appointment, schedule, booking, calendar, availability"
    message: "I'll connect you with our booking specialist..."
    
  - agent_id: "agent_def456uvw"
    name: "Technical Support"
    condition: "technical, broken, not working, error, issue"
    message: "Let me get our technical expert to help..."
    
  - agent_id: "agent_ghi789rst"
    name: "Billing Department"
    condition: "invoice, payment, charge, refund, billing"
    message: "I'll transfer you to our billing team..."

prompt_integration: |
  ## ADAPTABILITY
  Listen for transfer triggers:
  - Booking: "appointment", "schedule", "when can"
  - Support: "help", "broken", "not working"
  - Billing: "invoice", "charge", "payment"
  
  When transferring:
  1. Acknowledge the need
  2. Explain who they're being connected to
  3. Use the transfer message
  4. Pass context to next agent
```

#### Transfer Best Practices

```markdown
## TRANSFER CHECKLIST
- [ ] Natural language conditions (not regex)
- [ ] Specific trigger words/phrases
- [ ] Clear transfer messages
- [ ] Context preservation enabled
- [ ] First Message enabled on receiver
- [ ] No transfer loops possible
- [ ] Test each transfer path
```

### 3. Transfer to Number

**Purpose:** Escalate to human agents or external numbers

```yaml
tool_configuration:
  name: "transfer_to_number"
  enabled: true
  
numbers:
    - number: "+61400123456"
      name: "Emergency Line"
      condition: "emergency, urgent, critical, flood, fire"
      message: "This is urgent. Connecting you to emergency support..."
      
    - number: "+61400789012"
      name: "Senior Management"
      condition: "complaint, manager, supervisor, escalate"
      message: "I'll connect you with a supervisor..."
      
    - number: "+61400345678"
      name: "After Hours Support"
      condition: "after hours emergency"
      message: "Connecting you to after-hours support..."

prompt_integration: |
  ## ADAPTABILITY
  For emergency keywords (fire, flood, injury):
  - Immediately say: "This sounds like an emergency"
  - Transfer without delay
  - Stay on line until connected
  
  For escalation requests:
  - Acknowledge: "I understand you'd like to speak with someone"
  - Offer one attempt to resolve
  - If insisted, transfer immediately
```

### 4. Knowledge Base Integration

**Purpose:** Access and search information dynamically

```yaml
tool_configuration:
  name: "knowledge_base"
  enabled: true
  rag_enabled: true  # Retrieval-Augmented Generation
  
sources:
    - type: "documents"
      formats: ["PDF", "DOCX", "TXT", "HTML"]
      update_frequency: "daily"
      
    - type: "website"
      url: "https://docs.company.com"
      crawl_depth: 3
      
    - type: "database"
      connection: "api_endpoint"
      refresh: "real-time"

prompt_integration: |
  ## CONTEXT
  Knowledge base contains:
  - Product documentation
  - Pricing information
  - Policies and procedures
  - Technical specifications
  - FAQs and troubleshooting
  
  ## ADAPTABILITY
  When asked for information:
  1. Search knowledge base first
  2. If found, provide accurate answer
  3. If not found, acknowledge limitation
  4. Offer to connect with specialist
  
  Always cite source when sharing info:
  "According to our [document type]..."
```

#### Knowledge Base Best Practices

```markdown
## KNOWLEDGE BASE SETUP

### Document Preparation
1. Convert to supported formats (PDF, DOCX, TXT, HTML)
2. Structure with clear headings
3. Remove outdated information
4. Include metadata tags
5. Test search functionality

### RAG Configuration
- Enable for better search
- Set chunk size appropriately
- Configure relevance thresholds
- Test with common queries
- Monitor retrieval accuracy

### Maintenance
- Regular updates (weekly/monthly)
- Version control documents
- Archive old versions
- Track search failures
- Update based on gaps
```

### 5. Data Collection

**Purpose:** Gather structured information from customers

```yaml
tool_configuration:
  name: "data_collection"
  enabled: true
  
fields:
    - name: "customer_name"
      type: "string"
      required: true
      prompt: "May I have your full name?"
      validation: "min_length:2"
      
    - name: "email"
      type: "email"
      required: true
      prompt: "What's the best email to reach you?"
      validation: "email_format"
      
    - name: "phone"
      type: "phone"
      required: true
      prompt: "What's your phone number?"
      validation: "phone_format"
      
    - name: "appointment_date"
      type: "date"
      required: true
      prompt: "What date would you prefer?"
      validation: "future_date"
      
    - name: "appointment_time"
      type: "time"
      required: true
      prompt: "What time works best?"
      validation: "business_hours"
      
    - name: "service_type"
      type: "select"
      required: true
      options: ["Consultation", "Installation", "Repair", "Maintenance"]
      prompt: "What service do you need?"

prompt_integration: |
  ## GOAL
  Collect all required information for booking
  
  ## ADAPTABILITY
  When collecting data:
  - Ask one field at a time
  - Confirm each entry
  - Allow corrections
  - Validate in real-time
  - Summarize at end
  
  If validation fails:
  - Explain the issue clearly
  - Provide format example
  - Re-prompt politely
```

#### Data Collection Strategies

```markdown
## PROGRESSIVE COLLECTION

### Natural Flow
Instead of form-style:
"Let me get some details. First, your name?"
"Thanks John. And your email?"
"Perfect. What service do you need?"

### Smart Defaults
- Infer from context when possible
- Use caller ID for phone
- Suggest common options
- Pre-fill known information

### Validation Feedback
❌ "Invalid email"
✅ "That email seems to be missing the @ symbol"

❌ "Wrong format"
✅ "Phone numbers should be 10 digits, like 0412-345-678"
```

### 6. Webhook Integration

**Purpose:** Connect to external systems and APIs

```yaml
tool_configuration:
  name: "webhook"
  enabled: true
  
endpoints:
    - name: "create_ticket"
      url: "https://api.company.com/tickets"
      method: "POST"
      trigger: "support ticket creation"
      
    - name: "check_availability"
      url: "https://api.company.com/calendar"
      method: "GET"
      trigger: "appointment scheduling"
      
    - name: "update_crm"
      url: "https://api.company.com/crm"
      method: "PUT"
      trigger: "customer information update"

payload_template: |
  {
    "conversation_id": "{{system__conversation_id}}",
    "customer_phone": "{{system__caller_id}}",
    "timestamp": "{{system__time_utc}}",
    "agent_id": "{{system__agent_id}}",
    "collected_data": {
      "name": "{{customer_name}}",
      "email": "{{email}}",
      "issue": "{{issue_description}}"
    }
  }

error_handling:
  timeout: 5000
  retry_attempts: 2
  fallback: "manual_processing"
  
prompt_integration: |
  ## CONTEXT
  External systems available:
  - CRM for customer data
  - Calendar for scheduling
  - Ticketing for support
  
  ## ADAPTABILITY
  When webhook fails:
  - Acknowledge briefly
  - Collect information anyway
  - Promise manual follow-up
  - Provide reference number
```

#### Webhook Best Practices

```markdown
## WEBHOOK IMPLEMENTATION

### Security
- Use HTTPS only
- Implement authentication
- Validate SSL certificates
- Encrypt sensitive data
- Rate limit requests

### Reliability
- Set appropriate timeouts
- Implement retry logic
- Have fallback procedures
- Log all attempts
- Monitor success rates

### Testing
- Test with mock data
- Verify error handling
- Check timeout behavior
- Test under load
- Document expected responses
```

### 7. Language Detection

**Purpose:** Handle multi-lingual interactions

```yaml
tool_configuration:
  name: "detect_language"
  enabled: true
  
supported_languages:
    - code: "en"
      name: "English"
      agent: "agent_english_support"
      
    - code: "es"
      name: "Spanish"
      agent: "agent_spanish_support"
      
    - code: "zh"
      name: "Mandarin"
      agent: "agent_mandarin_support"

prompt_integration: |
  ## ADAPTABILITY
  If non-English detected:
  1. Acknowledge in English
  2. Ask: "Would you prefer [language]?"
  3. If yes, transfer to language-specific agent
  4. If no, continue in English
  
  Common phrases to detect:
  - Spanish: "hola", "necesito ayuda"
  - Mandarin: "你好", "需要帮助"
  - French: "bonjour", "j'ai besoin"
```

### 8. Skip Turn

**Purpose:** Allow customer to continue speaking

```yaml
tool_configuration:
  name: "skip_turn"
  enabled: true
  
use_cases:
    - "Customer is explaining complex issue"
    - "Emotional expression needs space"
    - "Gathering thoughts mid-sentence"
    - "Background conversation happening"

prompt_integration: |
  ## ADAPTABILITY
  Use skip turn when:
  - Customer says "wait", "hold on", "one second"
  - You hear background conversation
  - Customer is clearly not finished
  - Emotional moments need space
  
  Don't interrupt when:
  - Customer is venting frustration
  - Explaining medical symptoms
  - Providing detailed instructions
  - Reading reference numbers
```

---

## Custom Tool Development

### Creating Custom Tools

```javascript
// Example: Custom Tool Definition
{
  "tool_name": "check_inventory",
  "description": "Check product availability in real-time",
  "type": "webhook",
  "configuration": {
    "endpoint": "https://api.company.com/inventory",
    "method": "GET",
    "parameters": {
      "product_id": "required",
      "location": "optional"
    },
    "response_handling": {
      "success": "Product is available",
      "failure": "Unable to check availability",
      "parse": "json.availability"
    }
  },
  "prompt_integration": `
    When customer asks about availability:
    1. Get product name/ID
    2. Check inventory using tool
    3. Provide availability status
    4. Offer alternatives if unavailable
  `
}
```

### Tool Chaining

```yaml
complex_workflow:
  name: "Complete Booking Flow"
  steps:
    1:
      tool: "check_availability"
      input: "requested_date"
      output: "available_slots"
      
    2:
      tool: "data_collection"
      input: "customer_details"
      output: "booking_info"
      
    3:
      tool: "webhook"
      input: "booking_info"
      output: "confirmation_number"
      
    4:
      tool: "send_confirmation"
      input: "confirmation_details"
      output: "success_status"

error_handling:
  any_step_fails: "Collect manually, promise callback"
```

---

## Integration Patterns

### Pattern 1: Simple Router with Transfer

```markdown
## TOOLS ENABLED
- transfer_to_ai_agent (3 specialists)
- transfer_to_number (emergency only)
- end_call

## INTEGRATION
Router identifies need → Transfer to specialist → Specialist handles → End call
```

### Pattern 2: Data Collection with CRM

```markdown
## TOOLS ENABLED
- data_collection (customer info)
- webhook (CRM update)
- knowledge_base (product info)
- end_call

## INTEGRATION
Greet → Collect data → Search knowledge → Update CRM → Confirm → End
```

### Pattern 3: Multi-lingual Support Center

```markdown
## TOOLS ENABLED
- detect_language
- transfer_to_ai_agent (language-specific)
- knowledge_base (multi-language)
- escalation to human

## INTEGRATION
Detect language → Route to appropriate agent → Provide support → Escalate if needed
```

### Pattern 4: Complete Sales Flow

```markdown
## TOOLS ENABLED
- data_collection (lead info)
- webhook (CRM, calendar)
- knowledge_base (product catalog)
- transfer_to_number (sales manager)
- payment processing

## INTEGRATION
Qualify lead → Present solution → Check availability → Process payment → Confirm
```

---

## Testing Tools

### Tool Testing Protocol

```markdown
## TESTING CHECKLIST

### 1. Individual Tool Testing
- [ ] Enable one tool at a time
- [ ] Test positive triggers
- [ ] Test negative cases
- [ ] Verify error handling
- [ ] Check timeout behavior

### 2. Integration Testing
- [ ] Test tool combinations
- [ ] Verify data passing
- [ ] Check failure cascades
- [ ] Test rollback procedures
- [ ] Confirm logging

### 3. Load Testing
- [ ] Concurrent tool usage
- [ ] API rate limits
- [ ] Timeout under load
- [ ] Queue management
- [ ] Resource utilization

### 4. User Experience Testing
- [ ] Natural trigger detection
- [ ] Smooth transitions
- [ ] Clear error messages
- [ ] Appropriate fallbacks
- [ ] Recovery procedures
```

### Common Tool Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Transfer loops | Agents transfer back and forth | Add loop detection logic |
| Webhook timeout | Slow API response | Increase timeout, add async |
| Data loss | Collection interrupted | Save progressively |
| Knowledge not found | Poor search terms | Improve query parsing |
| Wrong transfer | Vague conditions | Make triggers specific |
| Tool not triggering | Condition too strict | Broaden trigger phrases |

---

## Best Practices

### Tool Selection

```markdown
## ESSENTIAL TOOLS BY AGENT TYPE

### Router/Receptionist
✅ transfer_to_ai_agent
✅ transfer_to_number (emergency)
✅ end_call
❌ Complex data collection
❌ Heavy webhook usage

### Support Agent
✅ knowledge_base
✅ data_collection (tickets)
✅ webhook (ticketing system)
✅ transfer_to_number (escalation)
✅ end_call

### Sales Agent
✅ data_collection (lead capture)
✅ webhook (CRM)
✅ knowledge_base (products)
✅ calendar integration
✅ transfer_to_number (closer)

### Emergency Handler
✅ transfer_to_number (immediate)
✅ skip_turn (let them talk)
✅ minimal other tools
```

### Tool Configuration Tips

1. **Start Simple**
   - Enable minimum tools first
   - Add complexity gradually
   - Test each addition

2. **Clear Triggers**
   - Use natural language
   - Multiple trigger phrases
   - Avoid regex/patterns

3. **Graceful Failures**
   - Always have fallbacks
   - Clear error messages
   - Manual alternatives

4. **Performance First**
   - Minimize tool calls
   - Cache when possible
   - Async where appropriate

5. **User Experience**
   - Natural integration
   - Transparent actions
   - Quick responses

---

## Monitoring and Analytics

### Tool Metrics

```yaml
tracking_metrics:
  usage:
    - Tool trigger frequency
    - Success/failure rates
    - Average execution time
    - Error types and frequency
    
  performance:
    - Response times
    - Timeout occurrences
    - API availability
    - Resource consumption
    
  business:
    - Conversion impact
    - Escalation rates
    - Data collection completion
    - Transfer success rates
```

### Optimization Cycle

```markdown
## MONTHLY TOOL REVIEW

1. Analyze tool usage statistics
2. Review failure logs
3. Check user feedback
4. Identify underused tools
5. Test new integrations
6. Update trigger conditions
7. Refine error handling
8. Document changes
```

---

## Security Considerations

### Tool Security Checklist

```markdown
## SECURITY REQUIREMENTS

### API Security
- [ ] HTTPS only for webhooks
- [ ] API key rotation
- [ ] IP whitelisting
- [ ] Rate limiting
- [ ] Request signing

### Data Protection
- [ ] Encrypt sensitive data
- [ ] No credentials in prompts
- [ ] Audit logging
- [ ] PII handling compliance
- [ ] Data retention policies

### Access Control
- [ ] Tool permission levels
- [ ] Agent-specific restrictions
- [ ] Admin approval for changes
- [ ] Regular security audits
- [ ] Incident response plan
```

---

*Next: Configure knowledge bases and RAG → [09-KNOWLEDGE_BASE_RAG.md](09-KNOWLEDGE_BASE_RAG.md)*