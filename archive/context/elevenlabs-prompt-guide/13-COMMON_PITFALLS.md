# Common Pitfalls and How to Avoid Them

## Overview

This guide covers the most common mistakes when building ElevenLabs agents and provides specific solutions to avoid them. Learn from others' experiences to build better agents faster.

## Critical Pitfalls

### 1. The Double Underscore Disaster

#### ❌ THE PROBLEM
```markdown
## WRONG - Single Underscore
{{system_time}}
{{system_timezone}}
{{system_caller_id}}

Result: Variables display as literal text
Impact: Agent says "The time is {{system_time}}"
```

#### ✅ THE SOLUTION
```markdown
## CORRECT - Double Underscore
{{system__time}}
{{system__timezone}}
{{system__caller_id}}

Result: Variables replaced with values
Impact: Agent says "The time is 2:30 PM"
```

#### Prevention Checklist
- [ ] Search and replace all single underscores
- [ ] Test every variable in dashboard
- [ ] Document the correct syntax prominently
- [ ] Review before every deployment

---

### 2. Transfer Loop Hell

#### ❌ THE PROBLEM
```yaml
agent_routing:
  sales_agent:
    transfers_to: ["support", "router"]
  support_agent:
    transfers_to: ["sales", "router"]
  router:
    transfers_to: ["sales", "support"]
    
# Result: Customer bounces between agents endlessly
```

#### ✅ THE SOLUTION
```yaml
loop_prevention:
  track_path: true
  max_transfers: 2
  
  rules:
    - name: "No back-transfer"
      if: "previous_agent == target_agent"
      then: "block_transfer"
      
    - name: "Max limit reached"
      if: "transfer_count >= 2"
      then: "escalate_to_human"
      
  prompt_integration: |
    ## ADAPTABILITY
    Previous agents: {{agent_path}}
    If target in path: Don't transfer back
    If 3rd transfer: Escalate to human
```

---

### 3. First Message Not Enabled

#### ❌ THE PROBLEM
```yaml
receiving_agent:
  first_message:
    enabled: false  # Or forgotten entirely
    
# Result: Dead silence after transfer
# Customer: "Hello? Anyone there?"
```

#### ✅ THE SOLUTION
```yaml
receiving_agent:
  first_message:
    enabled: true  # CRITICAL!
    text: "Hi! I understand you need help with [topic]."
    
  verification_checklist:
    - [ ] First Message toggle ON
    - [ ] Message text configured
    - [ ] Test transfer works
    - [ ] No dead air
```

---

### 4. Vague Transfer Conditions

#### ❌ THE PROBLEM
```markdown
## BAD TRANSFER CONDITIONS
"customer needs help" → Support
"has question" → Sales
"wants something" → Booking

Result: 90% incorrect routing
```

#### ✅ THE SOLUTION
```markdown
## GOOD TRANSFER CONDITIONS
Support: "technical issue, broken, not working, error, 
malfunction, stopped working, crashed, frozen"

Sales: "pricing, cost, purchase, buy, features, compare, 
discount, payment plans, trial, demo"

Booking: "appointment, schedule, book, availability, 
calendar, time slot, when can you, next available"
```

---

### 5. Knowledge Base Without RAG

#### ❌ THE PROBLEM
```yaml
knowledge_base:
  files_uploaded: true
  rag_enabled: false  # Forgotten!
  
# Result: Agent can't find any information
# Says: "I don't have that information"
```

#### ✅ THE SOLUTION
```yaml
knowledge_base:
  files_uploaded: true
  rag_enabled: true  # Essential!
  
  verification:
    - Upload documents
    - Enable RAG toggle
    - Test with queries
    - Verify retrieval works
```

---

## Prompt Engineering Pitfalls

### 6. Overcomplex Prompts

#### ❌ THE PROBLEM
```markdown
## OVERLY COMPLEX PROMPT
You are an AI assistant that helps customers with their 
inquiries about products and services while maintaining 
a professional demeanor and ensuring customer satisfaction 
through empathetic responses and accurate information 
delivery with a focus on building rapport and trust while 
also efficiently resolving issues and collecting necessary 
data for follow-up actions... [continues for 500 words]

Result: Agent confused, inconsistent behavior
```

#### ✅ THE SOLUTION
```markdown
## CLEAR, STRUCTURED PROMPT

## PERSONA
You are Sarah, a Customer Service Agent at ACME Corp.

## GOAL
PRIMARY: Resolve customer inquiries accurately.
SECONDARY: Collect contact info if unsure.

## TONE
Professional, friendly, concise.

Result: Clear, consistent behavior
```

---

### 7. Missing Adaptability Section

#### ❌ THE PROBLEM
```markdown
## PROMPT WITHOUT ADAPTABILITY
[Persona, Goal, Environment, Tone defined]
[No adaptability section]

Result: Can't handle angry customers, emergencies, or edge cases
```

#### ✅ THE SOLUTION
```markdown
## ADAPTABILITY
If customer angry:
  - Acknowledge frustration
  - Apologize for inconvenience
  - Offer quick resolution

If emergency mentioned:
  - Prioritize immediately
  - Transfer to emergency line
  - Stay on until connected
```

---

### 8. Hallucination Enablement

#### ❌ THE PROBLEM
```markdown
## DANGEROUS PROMPT
"Always provide an answer to the customer.
Never say you don't know.
Be helpful and give information."

Result: Agent makes up prices, policies, features
```

#### ✅ THE SOLUTION
```markdown
## SAFE PROMPT
"Only provide information from the knowledge base.
If information isn't available, acknowledge limitation.
Say: 'I don't have that specific information, but 
I can connect you with someone who does.'"
```

---

## Configuration Pitfalls

### 9. Wrong Model Selection

#### ❌ THE PROBLEM
```yaml
simple_router:
  model: "gemini-2.5-pro"  # Overkill!
  latency: "High"
  cost: "Expensive"
  
complex_support:
  model: "gemini-2.5-flash-lite"  # Underpowered!
  capability: "Insufficient"
```

#### ✅ THE SOLUTION
```yaml
simple_router:
  model: "gemini-2.5-flash-lite"
  reasoning: "Simple decisions, fast routing"
  
complex_support:
  model: "gemini-2.5-flash"  # or Pro
  reasoning: "Needs reasoning, knowledge"
```

---

### 10. Temperature Chaos

#### ❌ THE PROBLEM
```yaml
router_agent:
  temperature: 0.8  # Too creative!
  result: "Inconsistent routing"
  
emergency_handler:
  temperature: 0.7  # Too variable!
  result: "Different emergency instructions"
```

#### ✅ THE SOLUTION
```yaml
router_agent:
  temperature: 0.2
  reasoning: "Consistent routing needed"
  
emergency_handler:
  temperature: 0.1
  reasoning: "Critical consistency required"
  
sales_agent:
  temperature: 0.5
  reasoning: "Balance personality and reliability"
```

---

## Voice and Audio Pitfalls

### 11. Maximum Style Setting

#### ❌ THE PROBLEM
```yaml
voice_config:
  style: 1.0  # Maximum!
  result: "High latency, unnatural speech"
  customer: "Why does it sound so weird?"
```

#### ✅ THE SOLUTION
```yaml
voice_config:
  style: 0.0  # For real-time conversation
  reasoning: "Natural speech, low latency"
  
  # Only use style > 0 for:
  # - Pre-recorded messages
  # - Non-real-time generation
```

---

### 12. Wrong Audio Format

#### ❌ THE PROBLEM
```yaml
audio_output:
  format: "mp3_44100_192"  # High quality
  result: "300ms+ latency"
  impact: "Conversation feels sluggish"
```

#### ✅ THE SOLUTION
```yaml
audio_output:
  format: "pcm_16000"
  reasoning: "Optimal for real-time speech"
  latency: "< 100ms"
  quality: "Perfect for voice"
```

---

## Tool Configuration Pitfalls

### 13. Webhook Without Fallback

#### ❌ THE PROBLEM
```javascript
webhook_config: {
  url: "https://api.company.com/booking",
  timeout: 5000
  // No error handling!
}

// When webhook fails:
// Agent: *freezes* or *crashes*
```

#### ✅ THE SOLUTION
```javascript
webhook_config: {
  url: "https://api.company.com/booking",
  timeout: 5000,
  retry: 2,
  fallback: {
    on_failure: "collect_manually",
    message: "I'll note that down and have someone process it within the hour",
    action: "create_manual_ticket"
  }
}
```

---

### 14. Data Collection Without Validation

#### ❌ THE PROBLEM
```yaml
collect_email:
  type: "string"  # No validation!
  
# Customer: "My email is john"
# Agent: "Thank you!" *stores invalid email*
```

#### ✅ THE SOLUTION
```yaml
collect_email:
  type: "email"
  validation: "email_format"
  error_message: "That doesn't look like a complete email. Could you include the @ and domain?"
  example: "like john@example.com"
```

---

## Testing Pitfalls

### 15. Happy Path Only Testing

#### ❌ THE PROBLEM
```markdown
## TEST PLAN
1. Customer calls
2. Asks for booking
3. Provides all info correctly
4. Booking succeeds
✓ Done!

Reality: 80% of calls don't follow happy path
```

#### ✅ THE SOLUTION
```markdown
## COMPREHENSIVE TEST PLAN
- Happy path (20%)
- Invalid data (20%)
- Interruptions (15%)
- Transfers (15%)
- Errors/failures (10%)
- Angry customers (10%)
- Edge cases (10%)
```

---

### 16. No Load Testing

#### ❌ THE PROBLEM
```yaml
testing:
  unit_tests: "Complete"
  integration_tests: "Complete"
  load_tests: "Skipped - seems fine with 1 user"
  
# Launch day: 100 concurrent users
# Result: System crashes
```

#### ✅ THE SOLUTION
```yaml
testing:
  load_progression:
    - 1 user (baseline)
    - 10 users (small load)
    - 50 users (normal load)
    - 100 users (peak load)
    - 200 users (stress test)
    
  metrics:
    - Response time
    - Error rate
    - Resource usage
```

---

## Deployment Pitfalls

### 17. No Rollback Plan

#### ❌ THE PROBLEM
```markdown
## DEPLOYMENT
1. Update production agent
2. Issues discovered
3. Can't revert!
4. Customers impacted for hours
```

#### ✅ THE SOLUTION
```markdown
## SAFE DEPLOYMENT
1. Save current version
2. Deploy to staging first
3. Test thoroughly
4. Deploy to production
5. Monitor closely
6. Ready to rollback instantly

Rollback procedure documented and tested
```

---

### 18. Ignoring User Feedback

#### ❌ THE PROBLEM
```yaml
feedback_received:
  - "Agent talks too much"
  - "Can't understand accents"
  - "Transfers take forever"
  
action_taken: "None - metrics look fine"

Result: User satisfaction drops
```

#### ✅ THE SOLUTION
```yaml
feedback_process:
  weekly_review:
    - Analyze all feedback
    - Identify patterns
    - Prioritize fixes
    
  actions:
    - Reduce response length
    - Adjust voice clarity
    - Optimize transfer speed
    
  validation:
    - Test with users
    - Measure improvement
```

---

## Maintenance Pitfalls

### 19. Knowledge Base Decay

#### ❌ THE PROBLEM
```yaml
knowledge_base:
  last_updated: "6 months ago"
  contains:
    - Old prices
    - Discontinued products
    - Outdated policies
    
Result: Agent gives wrong information
```

#### ✅ THE SOLUTION
```yaml
maintenance_schedule:
  daily:
    - Check for urgent updates
    
  weekly:
    - Review common questions
    - Update FAQs
    
  monthly:
    - Full content review
    - Remove outdated info
    - Add new products/services
    
  quarterly:
    - Complete audit
    - Restructure if needed
```

---

### 20. Performance Degradation

#### ❌ THE PROBLEM
```markdown
## GRADUAL DEGRADATION
Month 1: Response time 1s
Month 2: Response time 1.5s
Month 3: Response time 2s
Month 6: Response time 4s

"It's always been a bit slow"
```

#### ✅ THE SOLUTION
```markdown
## PERFORMANCE MONITORING
Set baselines:
- Response time: < 2s
- Error rate: < 1%
- Transfer success: > 95%

Alerts when:
- 10% degradation
- Trend over 1 week
- Sudden spike

Monthly review:
- Compare to baseline
- Investigate changes
- Optimize proactively
```

---

## Quick Reference: Pitfall Prevention Checklist

### Before Development
- [ ] Clear requirements documented
- [ ] Success metrics defined
- [ ] Architecture planned
- [ ] Edge cases identified

### During Development
- [ ] Use double underscores for system variables
- [ ] Enable RAG for knowledge base
- [ ] Enable First Message on receivers
- [ ] Add loop prevention
- [ ] Include Adaptability section
- [ ] Set appropriate temperature
- [ ] Choose right model for task
- [ ] Add fallbacks for all tools

### Before Testing
- [ ] Test beyond happy path
- [ ] Include load testing
- [ ] Test all transfer paths
- [ ] Verify error handling
- [ ] Check voice quality

### Before Deployment
- [ ] Document rollback procedure
- [ ] Test in staging
- [ ] Monitor metrics baseline
- [ ] Prepare incident response

### After Deployment
- [ ] Monitor performance
- [ ] Review user feedback
- [ ] Update knowledge base
- [ ] Track quality metrics
- [ ] Continuous improvement

---

## Recovery Strategies

### When Things Go Wrong

```markdown
## INCIDENT RECOVERY PLAYBOOK

1. **Detect**
   - Monitoring alert
   - User complaint
   - Metric deviation

2. **Assess**
   - Severity level
   - User impact
   - Root cause

3. **Mitigate**
   - Quick fix if possible
   - Workaround if not
   - Rollback if necessary

4. **Communicate**
   - Update stakeholders
   - Inform users if needed
   - Document timeline

5. **Resolve**
   - Implement permanent fix
   - Test thoroughly
   - Deploy carefully

6. **Review**
   - Post-mortem meeting
   - Document lessons learned
   - Update prevention measures
```

---

## Learning from Failures

### Post-Mortem Template

```markdown
## INCIDENT POST-MORTEM

**Date:** [Date]
**Duration:** [How long]
**Impact:** [Users affected]

**What Happened:**
[Timeline of events]

**Root Cause:**
[Why it happened]

**What Went Well:**
- Quick detection
- Fast mitigation
- Good communication

**What Could Improve:**
- Better testing
- Earlier detection
- Clearer documentation

**Action Items:**
- [ ] Add monitoring for X
- [ ] Update test suite
- [ ] Document procedure
- [ ] Train team on Y

**Lessons Learned:**
[Key takeaways for future]
```

---

*Next: Advanced patterns and techniques → [14-ADVANCED_PATTERNS.md](14-ADVANCED_PATTERNS.md)*