# Variables and Dynamic Content in ElevenLabs System Prompts

## Critical Rule #1: Double Underscore

### ⚠️ THE MOST IMPORTANT RULE ⚠️

**System variables MUST use double underscore:**
- ✅ CORRECT: `{{system__time}}`
- ❌ WRONG: `{{system_time}}`
- ❌ WRONG: `{{system-time}}`
- ❌ WRONG: `{system__time}`

**This is the #1 cause of agent failures. Double-check every variable!**

---

## System Variables Reference

### Always Available Variables

These variables work in ALL agents without any configuration:

| Variable | Description | Example Output | Use Cases |
|----------|-------------|----------------|-----------|
| `{{system__time}}` | Local time in caller's timezone | "2:30 PM" | Business hours check |
| `{{system__timezone}}` | Caller's timezone | "Australia/Sydney" | Location awareness |
| `{{system__time_utc}}` | Current UTC time | "2024-01-15T04:30:00Z" | Logging, coordination |
| `{{system__caller_id}}` | Phone number calling | "+61412345678" | Caller identification |
| `{{system__conversation_id}}` | Unique conversation ID | "conv_abc123xyz789" | Tracking, debugging |
| `{{system__agent_id}}` | Current agent's ID | "agent_7701k2pr9ch5ee" | Multi-agent context |

### Variable Usage Examples

#### Time-Based Greeting
```markdown
## PERSONA
You are Emma, our receptionist.

## CONTEXT
- Current time: {{system__time}} ({{system__timezone}})

## ADAPTABILITY
If {{system__time}} is before 12 PM:
  Say: "Good morning!"
If {{system__time}} is between 12 PM and 5 PM:
  Say: "Good afternoon!"
If {{system__time}} is after 5 PM:
  Say: "Good evening!"
```

#### Business Hours Routing
```markdown
## CONTEXT
- Current time: {{system__time}} ({{system__timezone}})
- Business hours: 8 AM - 6 PM AEST Monday-Friday
- After-hours service: Emergency only

## ADAPTABILITY
Check if {{system__time}} is within business hours:
- If yes: "How can I help you today?"
- If no: "You've reached us after hours. Is this an emergency?"
```

#### Caller Recognition
```markdown
## CONTEXT
- Caller ID: {{system__caller_id}}
- If recognized, customer data will be available

## PERSONA
You are Sarah, a customer service representative.

## ADAPTABILITY
If {{system__caller_id}} is in our database:
  - Greet by name
  - Reference last interaction
  - Skip verification questions
If {{system__caller_id}} is unknown:
  - Standard greeting
  - Collect information
```

---

## Custom Variables (SDK/API Only)

### ⚠️ Important Limitations

**Custom variables ONLY work with:**
- SDK implementation (JavaScript, Python, etc.)
- API integration
- Server-side implementation

**They DON'T work with:**
- Simple embed widget ❌
- Dashboard testing interface ❌
- Direct agent links ❌

### SDK Implementation

#### JavaScript Example
```javascript
// Using ElevenLabs SDK
const conversation = await ElevenLabsConvai.startSession({
  agentId: 'agent_id',
  variables: {
    business_name: 'ACME Corp',
    business_hours_start: '09:00',
    business_hours_end: '17:00',
    emergency_number: '0400-123-456',
    special_offer: '20% off this week',
    manager_name: 'John Smith',
    location: 'Sydney CBD'
  }
});
```

#### Python Example
```python
# Using ElevenLabs Python SDK
conversation = ElevenLabs.start_conversation(
    agent_id="agent_id",
    variables={
        "business_name": "ACME Corp",
        "business_hours_start": "09:00",
        "business_hours_end": "17:00",
        "emergency_number": "0400-123-456",
        "special_offer": "20% off this week"
    }
)
```

#### Using Custom Variables in Prompts
```markdown
## PERSONA
You are a representative at {{business_name}}.

## CONTEXT
- Business hours: {{business_hours_start}} to {{business_hours_end}}
- Emergency contact: {{emergency_number}}
- Current promotion: {{special_offer}}
- Manager on duty: {{manager_name}}
- Location: {{location}}

## ADAPTABILITY
If asked about hours:
  Say: "We're open from {{business_hours_start}} to {{business_hours_end}}"
  
If emergency after hours:
  Say: "Please call our emergency line at {{emergency_number}}"
```

### Dashboard Placeholder Values

When testing in the dashboard, you can set placeholder values:
1. Go to Agent Settings → Variables
2. Add variable name and test value
3. These are ONLY for dashboard testing
4. Real values must come from SDK/API

---

## Dynamic Content Strategies

### 1. Time-Based Behavior

#### Business Hours Logic
```markdown
## CONTEXT
- Current time: {{system__time}}
- Day of week can be inferred from date
- Timezone: {{system__timezone}}

## BUSINESS HOURS
- Monday-Friday: 8:00 AM - 6:00 PM
- Saturday: 9:00 AM - 2:00 PM
- Sunday: Closed

## ADAPTABILITY
Determine if we're open:
1. Check current time against hours
2. If open: Proceed normally
3. If closed: Offer callback scheduling
4. If emergency: Provide emergency number
```

#### Appointment Scheduling
```markdown
## CONTEXT
- Current time: {{system__time}}
- Cannot schedule in the past
- Minimum 2 hours notice required

## SCHEDULING LOGIC
When scheduling:
1. Current time is {{system__time}}
2. Earliest available is 2 hours from now
3. Suggest times after this point
4. Confirm timezone with customer
```

### 2. Personalization

#### Returning Customer
```markdown
## CONTEXT
- Caller: {{system__caller_id}}
- Check CRM for history

## PERSONALIZATION
If {{system__caller_id}} has previous interactions:
  - "Welcome back! I see you called about [previous issue]"
  - "Has your [previous issue] been resolved?"
  - Skip basic information collection
```

#### Location-Based Service
```markdown
## CONTEXT
- Timezone indicates approximate location: {{system__timezone}}
- Australia/Sydney = NSW services
- Australia/Perth = WA services

## LOCATION SERVICES
Based on {{system__timezone}}:
- Offer nearest branch location
- Quote local service times
- Mention regional promotions
```

### 3. Conversation Tracking

#### Multi-Step Processes
```markdown
## CONTEXT
- Conversation ID: {{system__conversation_id}}
- Use for tracking multi-step processes

## PROCESS TRACKING
"Your reference number is {{system__conversation_id}}"
"Please save this for your records"
"Use this if you need to call back"
```

#### Quality Assurance
```markdown
## CONTEXT
- All conversations logged with {{system__conversation_id}}
- Agent performance tracked via {{system__agent_id}}

## QA MENTIONS
At end of call:
"This conversation ({{system__conversation_id}}) may be 
recorded for quality assurance"
```

---

## Advanced Variable Techniques

### 1. Computed Variables

While you can't create computed variables directly, you can instruct the agent to derive information:

```markdown
## CONTEXT
- Current time: {{system__time}}
- Business closes at 6:00 PM

## ADAPTABILITY
Calculate remaining business hours:
- If {{system__time}} is 4:30 PM, we have 1.5 hours left
- If less than 30 minutes until closing, mention this
- If less than 1 hour, offer next-day service
```

### 2. Conditional Logic Chains

```markdown
## CONTEXT
- Time: {{system__time}}
- Caller: {{system__caller_id}}

## COMPLEX LOGIC
Step 1: Check if business hours
  If yes → Step 2
  If no → Offer emergency or callback

Step 2: Check if existing customer ({{system__caller_id}})
  If yes → Personalized greeting
  If no → New customer onboarding

Step 3: Based on time until closing
  If > 2 hours → Full service
  If < 2 hours → Quick service only
  If < 30 min → Next day scheduling
```

### 3. Fallback Strategies

```markdown
## VARIABLE HANDLING
If {{system__caller_id}} is not available:
  - Don't mention caller ID
  - Ask for phone number manually
  - Proceed with standard verification

If {{system__timezone}} is unclear:
  - Ask customer for their location
  - Default to AEST for Australian businesses
  - Confirm timezone for appointments
```

---

## Variable Best Practices

### Do's ✅

1. **Always Test Variables**
   ```markdown
   Test each variable:
   - In dashboard with placeholders
   - In production with real values
   - With missing/null values
   ```

2. **Provide Fallbacks**
   ```markdown
   If variable is empty or undefined:
   - Have alternative text ready
   - Don't break the conversation
   - Log for debugging
   ```

3. **Document Variable Usage**
   ```markdown
   ## VARIABLES USED
   - {{system__time}}: For greetings and hours
   - {{system__caller_id}}: For personalization
   - {{business_hours}}: Custom, from SDK
   ```

4. **Use Clear Naming**
   ```markdown
   Good: {{business_hours_start}}
   Bad: {{bhs}} or {{start}}
   ```

### Don'ts ❌

1. **Don't Use Variables in First Message**
   ```markdown
   ❌ BAD First Message:
   "Hi {{customer_name}}, calling at {{system__time}}"
   
   ✅ GOOD First Message:
   "Hello, thank you for calling ACME Corp"
   ```

2. **Don't Assume Variables Exist**
   ```markdown
   ❌ BAD:
   "Your account {{account_number}} shows..."
   
   ✅ GOOD:
   "Let me look up your account..." [then check if exists]
   ```

3. **Don't Mix Variable Syntaxes**
   ```markdown
   ❌ BAD:
   {{system_time}} or ${system__time} or {system__time}
   
   ✅ GOOD:
   {{system__time}} (always double braces, double underscore)
   ```

---

## Debugging Variable Issues

### Common Problems and Solutions

| Problem | Cause | Solution |
|---------|-------|----------|
| Variable shows as literal text | Wrong syntax | Check double underscore |
| Variable is empty | Not available in context | Add fallback handling |
| Time is wrong | Timezone issue | Use {{system__timezone}} |
| Caller ID missing | Anonymous caller | Handle gracefully |
| Custom var not working | Using simple embed | Switch to SDK |

### Debug Checklist

```markdown
## Variable Debugging Steps
1. [ ] Verify double underscore syntax
2. [ ] Check if system or custom variable
3. [ ] Test in dashboard with placeholders
4. [ ] Confirm SDK passes variables correctly
5. [ ] Add console.log/print for variables
6. [ ] Check agent logs for variable values
7. [ ] Test with missing variables
8. [ ] Verify timezone handling
```

### Testing Template

```markdown
## VARIABLE TEST PROMPT
Test all variables:
- System time: {{system__time}}
- Timezone: {{system__timezone}}
- UTC time: {{system__time_utc}}
- Caller ID: {{system__caller_id}}
- Conversation: {{system__conversation_id}}
- Agent: {{system__agent_id}}

Say each value out loud to verify.
```

---

## Real-World Examples

### Example 1: Restaurant Booking System
```markdown
## CONTEXT
- Current time: {{system__time}} ({{system__timezone}})
- Restaurant hours: 11:00 AM - 10:00 PM
- Last seating: 9:00 PM
- Kitchen closes: 9:30 PM

## BOOKING LOGIC
When {{system__time}} is:
- Before 11 AM: "We open at 11, shall I book lunch?"
- 11 AM - 2 PM: Lunch service available
- 2 PM - 5 PM: Limited menu period
- 5 PM - 9 PM: Full dinner service
- After 9 PM: "Kitchen closing soon, tomorrow?"
```

### Example 2: Technical Support Triage
```markdown
## CONTEXT
- Conversation ID: {{system__conversation_id}}
- Support ticket will use this ID
- Caller: {{system__caller_id}}

## SUPPORT FLOW
1. "Your case number is {{system__conversation_id}}"
2. Check if {{system__caller_id}} has open tickets
3. Priority based on time of day ({{system__time}}):
   - Business hours: Normal priority
   - After hours: Emergency only
   - Weekend: Callback Monday
```

### Example 3: Appointment Reminder System
```markdown
## CONTEXT
- Call time: {{system__time}}
- Patient phone: {{system__caller_id}}

## REMINDER SCRIPT
"This is a reminder from Melbourne Medical Centre"
"Calling {{system__caller_id}} at {{system__time}}"
"Your appointment is tomorrow at [appointment time]"
"Reference: {{system__conversation_id}}"
```

---

## Integration with Other Features

### With Multi-Agent Systems
```markdown
## AGENT CONTEXT
- Current agent: {{system__agent_id}}
- When transferring, pass conversation context
- New agent sees same {{system__conversation_id}}
```

### With Data Collection
```markdown
## COLLECT WITH CONTEXT
- Tag all data with {{system__conversation_id}}
- Timestamp with {{system__time_utc}}
- Associate with {{system__caller_id}}
```

### With Webhooks
```javascript
// Send variables to webhook
webhook_data = {
  conversation_id: "{{system__conversation_id}}",
  caller_id: "{{system__caller_id}}",
  timestamp: "{{system__time_utc}}",
  agent_id: "{{system__agent_id}}"
}
```

---

## Migration Guide

### From Single to Double Underscore

If migrating from old syntax:

```markdown
## FIND AND REPLACE
Find: {{system_time}}
Replace: {{system__time}}

Find: {{system_timezone}}
Replace: {{system__timezone}}

Find: {{system_caller_id}}
Replace: {{system__caller_id}}
```

### From Hardcoded to Dynamic

```markdown
## BEFORE (Hardcoded)
"Our office hours are 9 AM to 5 PM"

## AFTER (Dynamic)
"Our office hours are {{business_hours_start}} to {{business_hours_end}}"
```

---

*Next: Design multi-agent systems → [06-MULTI_AGENT_ARCHITECTURE.md](06-MULTI_AGENT_ARCHITECTURE.md)*