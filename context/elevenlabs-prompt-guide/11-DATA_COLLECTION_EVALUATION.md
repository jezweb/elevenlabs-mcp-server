# Data Collection and Evaluation Guide for ElevenLabs Agents

## Overview

Data collection enables agents to gather structured information from users, while evaluation criteria measure agent performance and conversation quality. Together, they provide insights for continuous improvement.

## Data Collection Configuration

### Data Types

| Type | Use For | Validation | Example |
|------|---------|------------|---------|
| **String** | Names, text | Length, pattern | "John Smith" |
| **Boolean** | Yes/No | True/False | true |
| **Integer** | Whole numbers | Range, min/max | 42 |
| **Number** | Decimals | Precision, range | 99.95 |
| **Email** | Email addresses | Format validation | "john@example.com" |
| **Phone** | Phone numbers | Format, country | "+61412345678" |
| **Date** | Calendar dates | Past/future | "2024-03-15" |
| **Time** | Time values | Business hours | "14:30" |
| **Select** | Multiple choice | Predefined options | "Option A" |

### Basic Data Collection Setup

```yaml
data_collection:
  enabled: true
  
  fields:
    customer_name:
      type: "string"
      required: true
      min_length: 2
      max_length: 100
      prompt: "May I have your full name, please?"
      confirmation: "Thank you, {value}"
      
    email_address:
      type: "email"
      required: true
      prompt: "What's the best email address to reach you?"
      validation_message: "Please provide a valid email like name@example.com"
      
    phone_number:
      type: "phone"
      required: true
      format: "australian"
      prompt: "And your phone number?"
      example: "Like 0412-345-678"
      
    appointment_date:
      type: "date"
      required: true
      constraints:
        min: "today"
        max: "today + 30 days"
        exclude_weekends: true
      prompt: "What date works best for you?"
      
    service_type:
      type: "select"
      required: true
      options:
        - "Installation"
        - "Repair"
        - "Maintenance"
        - "Consultation"
      prompt: "What type of service do you need?"
```

### Progressive Data Collection

```markdown
## NATURAL COLLECTION FLOW

Instead of form-style questioning, make it conversational:

### Bad ❌
"I need to collect some information.
What is your name?
What is your email?
What is your phone number?"

### Good ✅
"I'd be happy to help you book that appointment. 
Let me get a few details to set that up.
First, could I get your name?"

[After response]
"Thanks, John. And what's the best email for 
sending the confirmation?"

[After response]
"Perfect. And a phone number in case we need 
to reach you about the appointment?"
```

### Conditional Data Collection

```yaml
conditional_collection:
  base_fields:
    - name
    - contact_method
    
  conditional_logic:
    if_contact_method_email:
      collect: "email_address"
      skip: "phone_number"
      
    if_contact_method_phone:
      collect: "phone_number"
      skip: "email_address"
      
    if_contact_method_both:
      collect: ["email_address", "phone_number"]
      
    if_service_type_installation:
      collect: ["address", "property_type", "access_instructions"]
      
    if_service_type_consultation:
      collect: ["preferred_meeting_type", "timezone"]
```

### Data Validation Strategies

```markdown
## VALIDATION APPROACHES

### Real-Time Validation
Validate as user provides information:

"Let me make sure I have your email correct...
john.smith@gmail... that doesn't look complete.
Could you provide the full email address?"

### Format Guidance
Provide format before they answer:

"I'll need your phone number. Please include 
the area code, like 02-1234-5678 or 0412-345-678"

### Gentle Correction
When validation fails:

❌ "Invalid input"
✅ "I didn't quite catch that phone number. 
Could you say it again with the area code?"

### Confirmation Loop
Always confirm critical data:

"Let me confirm: Your email is john@example.com 
and phone is 0412-345-678. Is that correct?"
```

---

## Evaluation Criteria Configuration

### Understanding Evaluation Criteria

Evaluation criteria are post-conversation assessments that measure specific aspects of agent performance.

```yaml
evaluation_basics:
  when: "After each conversation"
  who: "LLM analyzes transcript"
  what: "Specific success/failure conditions"
  why: "Track performance and identify improvements"
  
  output:
    - success: boolean
    - failure: boolean
    - unknown: boolean
    - rationale: string
```

### Single Evaluation Criterion

```yaml
evaluation_criteria:
  name: "Correct Issue Resolution"
  
  description: "Did the agent correctly identify and resolve the customer's issue?"
  
  success_conditions:
    - "Issue was identified correctly"
    - "Appropriate solution provided"
    - "Customer confirmed resolution"
    - "No further assistance needed"
    
  failure_conditions:
    - "Issue misidentified"
    - "Wrong solution provided"
    - "Customer still has problem"
    - "Had to escalate unresolved"
    
  unknown_conditions:
    - "Conversation ended abruptly"
    - "Unclear if resolved"
    - "Customer didn't confirm"
```

### Multiple Evaluation Criteria

```yaml
agent_evaluation_set:
  routing_accuracy:
    name: "Accurate Routing"
    measure: "Did agent route to correct department?"
    success: "Routed to appropriate specialist"
    failure: "Routed incorrectly or failed to route"
    
  response_time:
    name: "Quick Response"
    measure: "Did agent respond quickly?"
    success: "Identified need within 30 seconds"
    failure: "Took over 1 minute to understand"
    
  professionalism:
    name: "Professional Interaction"
    measure: "Was the agent professional?"
    success: "Polite, helpful, appropriate tone"
    failure: "Rude, dismissive, or inappropriate"
    
  data_completeness:
    name: "Complete Data Collection"
    measure: "Did agent collect all required information?"
    success: "All fields collected and validated"
    failure: "Missing required information"
```

### Evaluation by Agent Type

#### Router Agent Evaluation
```yaml
router_evaluation:
  criteria_1:
    name: "Routing Speed"
    success: "Routed within 30 seconds"
    failure: "Took over 1 minute"
    weight: 0.4
    
  criteria_2:
    name: "Routing Accuracy"
    success: "Sent to correct specialist"
    failure: "Sent to wrong department"
    weight: 0.4
    
  criteria_3:
    name: "Emergency Detection"
    success: "Identified emergencies correctly"
    failure: "Missed emergency indicators"
    weight: 0.2
```

#### Support Agent Evaluation
```yaml
support_evaluation:
  criteria_1:
    name: "Problem Resolution"
    success: "Issue resolved or properly escalated"
    failure: "Issue unresolved without escalation"
    weight: 0.35
    
  criteria_2:
    name: "Technical Accuracy"
    success: "Provided correct technical information"
    failure: "Gave incorrect instructions"
    weight: 0.35
    
  criteria_3:
    name: "Customer Satisfaction"
    success: "Customer expressed satisfaction"
    failure: "Customer frustrated or dissatisfied"
    weight: 0.3
```

#### Sales Agent Evaluation
```yaml
sales_evaluation:
  criteria_1:
    name: "Lead Qualification"
    success: "Properly qualified lead with BANT"
    failure: "Failed to qualify or missed key info"
    weight: 0.25
    
  criteria_2:
    name: "Product Knowledge"
    success: "Accurate product information provided"
    failure: "Incorrect or misleading information"
    weight: 0.25
    
  criteria_3:
    name: "Conversion Progress"
    success: "Moved lead forward in sales process"
    failure: "Lead went backwards or dropped"
    weight: 0.3
    
  criteria_4:
    name: "Follow-up Scheduled"
    success: "Next steps clearly defined"
    failure: "No follow-up arranged"
    weight: 0.2
```

---

## Advanced Data Collection Patterns

### Multi-Step Forms

```yaml
multi_step_booking:
  step_1_basic:
    fields: ["name", "email", "phone"]
    transition: "Great! Now let's find a time..."
    
  step_2_service:
    fields: ["service_type", "urgency"]
    transition: "I understand what you need..."
    
  step_3_scheduling:
    fields: ["preferred_date", "preferred_time"]
    transition: "Let me check availability..."
    
  step_4_confirmation:
    review_all: true
    confirm: "Let me confirm everything..."
    
  error_recovery:
    on_abandon: "Save progress for callback"
    on_timeout: "Offer to email form link"
```

### Dependent Field Collection

```javascript
// Dynamic field requirements
const getRequiredFields = (serviceType) => {
  const baseFields = ['name', 'contact'];
  
  switch(serviceType) {
    case 'delivery':
      return [...baseFields, 'address', 'delivery_instructions'];
      
    case 'pickup':
      return [...baseFields, 'pickup_time', 'vehicle_details'];
      
    case 'virtual':
      return [...baseFields, 'email', 'timezone', 'platform_preference'];
      
    default:
      return baseFields;
  }
};
```

### Smart Defaults and Inference

```markdown
## INTELLIGENT COLLECTION

### Use Available Information
If caller_id is available:
"I see you're calling from 0412-345-678. 
Should I use this number for contact?"

### Infer from Context
If customer mentions morning:
"So you prefer morning appointments. 
How about 9 AM or 10 AM?"

### Remember Previous Answers
If collected email:
"Should I send the confirmation to 
john@example.com that you just provided?"

### Suggest Common Options
For appointment times:
"Most customers prefer 10 AM or 2 PM. 
Would either of those work?"
```

---

## Data Privacy and Compliance

### Sensitive Data Handling

```yaml
sensitive_data_rules:
  never_collect:
    - full_credit_card_number
    - social_security_number
    - passwords
    - pin_codes
    - security_questions
    
  collect_with_care:
    - date_of_birth:
        only_when: "age_verification_required"
        storage: "encrypted"
        retention: "minimum_required"
        
    - medical_information:
        only_when: "healthcare_context"
        compliance: "HIPAA"
        consent: "required"
        
  pii_handling:
    - announce_collection: true
    - explain_usage: true
    - offer_opt_out: where_possible
    - secure_transmission: always
    - retention_policy: defined
```

### Compliance Statements

```markdown
## PRIVACY NOTICES IN CONVERSATION

### Before Collection
"I'll need to collect some information to assist you. 
This will be used only for your service request and 
handled according to our privacy policy."

### For Sensitive Data
"For security verification, I need to ask for your 
date of birth. This is only used to verify your 
identity and is not stored."

### Data Usage
"The information you provide will be used to:
- Process your appointment
- Send confirmation
- Contact you if needed
Is that okay?"

### Right to Refuse
"If you prefer not to provide this information, 
I can arrange for you to complete this process 
via our secure website instead."
```

---

## Evaluation Analytics and Reporting

### Performance Metrics Dashboard

```yaml
evaluation_metrics:
  daily_summary:
    total_conversations: 847
    evaluated: 823
    
    success_rates:
      routing_accuracy: 94%
      issue_resolution: 87%
      data_completion: 91%
      customer_satisfaction: 89%
      
    failures_by_type:
      wrong_routing: 23
      incomplete_data: 31
      unresolved_issues: 45
      poor_satisfaction: 38
      
  trends:
    improving: ["routing_accuracy", "data_completion"]
    declining: ["issue_resolution"]
    stable: ["customer_satisfaction"]
```

### Evaluation Report Template

```markdown
## WEEKLY EVALUATION REPORT

### Executive Summary
- Overall Success Rate: 88.5% (↑ 2.3%)
- Total Conversations: 5,234
- Critical Failures: 14

### By Agent Type
| Agent | Conversations | Success | Top Issue |
|-------|--------------|---------|-----------|
| Router | 2,100 | 94% | Speed |
| Support | 1,890 | 86% | Resolution |
| Sales | 844 | 83% | Qualification |
| Booking | 400 | 92% | Availability |

### Key Insights
1. Router performance improved after condition updates
2. Support resolution dropped - needs knowledge base update
3. Sales qualification needs additional training prompts

### Action Items
- [ ] Update support agent knowledge base
- [ ] Refine sales qualification questions
- [ ] Review failed routing cases
- [ ] Implement additional evaluation criteria
```

### Correlation Analysis

```yaml
correlation_findings:
  high_correlation:
    - fast_routing ↔ customer_satisfaction (0.82)
    - complete_data ↔ successful_booking (0.91)
    - professional_tone ↔ issue_resolution (0.76)
    
  negative_correlation:
    - multiple_transfers ↔ satisfaction (-0.84)
    - long_wait ↔ completion_rate (-0.72)
    
  insights:
    - "Speed matters more than perfection"
    - "Complete data collection critical for bookings"
    - "Transfer loops destroy satisfaction"
```

---

## Testing Data Collection and Evaluation

### Data Collection Test Cases

```markdown
## TEST SCENARIOS

### Happy Path
1. Provide all data correctly first time
2. Verify smooth progression
3. Confirm data saved correctly

### Validation Testing
1. Provide invalid email (missing @)
2. Verify gentle correction
3. Provide valid email
4. Confirm acceptance

### Interruption Handling
1. Start data collection
2. Interrupt with question
3. Verify agent returns to collection
4. Complete collection

### Abandonment Recovery
1. Start collection
2. Say "I need to go"
3. Verify save progress offer
4. Confirm callback arrangement
```

### Evaluation Criteria Testing

```markdown
## EVALUATION TEST PROTOCOL

### Test Each Criterion
For each evaluation criterion:
1. Create conversation meeting success conditions
2. Verify marked as success
3. Create conversation meeting failure conditions
4. Verify marked as failure
5. Create ambiguous conversation
6. Verify marked as unknown

### Edge Cases
- Very short conversations
- Transferred conversations
- Abandoned conversations
- Multiple issue conversations
- Emergency situations

### Accuracy Verification
Sample 100 conversations:
- Manual review by human
- Compare with automated evaluation
- Calculate accuracy percentage
- Identify systematic errors
- Refine evaluation criteria
```

---

## Integration with Other Systems

### CRM Integration

```javascript
// Send collected data to CRM
const updateCRM = async (collectedData) => {
  const crmPayload = {
    contact: {
      name: collectedData.customer_name,
      email: collectedData.email_address,
      phone: collectedData.phone_number
    },
    opportunity: {
      service: collectedData.service_type,
      value: collectedData.estimated_value,
      stage: 'qualification'
    },
    metadata: {
      source: 'ai_agent',
      agent_id: collectedData.agent_id,
      conversation_id: collectedData.conversation_id,
      evaluation_scores: collectedData.evaluation_results
    }
  };
  
  return await crmAPI.createOrUpdate(crmPayload);
};
```

### Analytics Platform

```yaml
analytics_integration:
  data_points:
    - conversation_id
    - timestamp
    - duration
    - fields_collected
    - validation_failures
    - evaluation_scores
    
  events:
    - collection_started
    - field_validated
    - collection_completed
    - evaluation_complete
    
  real_time_dashboards:
    - collection_success_rate
    - average_collection_time
    - validation_error_rate
    - evaluation_trends
```

---

## Best Practices

### Data Collection Do's ✅
- Make collection conversational
- Validate gently and helpfully
- Confirm critical information
- Save progress incrementally
- Provide format examples
- Use smart defaults
- Handle interruptions gracefully
- Respect privacy concerns

### Data Collection Don'ts ❌
- Don't collect unnecessary data
- Don't be robotic or formal
- Don't repeat questions
- Don't lose collected data
- Don't ignore validation
- Don't rush the customer
- Don't collect sensitive data insecurely

### Evaluation Do's ✅
- Define clear success criteria
- Use multiple evaluation points
- Weight criteria appropriately
- Review and refine regularly
- Correlate with business outcomes
- Track trends over time
- Act on insights

### Evaluation Don'ts ❌
- Don't over-complicate criteria
- Don't ignore edge cases
- Don't set impossible standards
- Don't evaluate without action
- Don't forget human review
- Don't measure vanity metrics

---

## Optimization Strategies

### Improving Collection Rates

```markdown
## OPTIMIZATION TECHNIQUES

### Reduce Fields
Only collect what's absolutely necessary:
- Required now: Name, contact, issue
- Can get later: Preferences, details

### Progressive Disclosure
Start simple, add complexity:
1. "What's your name?" (easy)
2. "Best phone number?" (easy)
3. "Describe the issue" (harder)

### Smart Timing
Collect at natural points:
- After building rapport
- When customer is engaged
- Before complex discussions

### Recovery Options
When collection fails:
- Offer form email
- Schedule callback
- Collect minimum for follow-up
```

### Enhancing Evaluation Accuracy

```yaml
accuracy_improvements:
  clearer_criteria:
    before: "Good customer service"
    after: "Greeted within 5 seconds, used name, thanked customer"
    
  specific_conditions:
    before: "Resolved issue"
    after: "Customer confirmed issue fixed and no further help needed"
    
  edge_case_handling:
    add: "unknown" category for ambiguous cases
    review: Weekly human review of "unknown" cases
    refine: Update criteria based on patterns
```

---

*Next: Testing and quality assurance → [12-TESTING_AND_QUALITY.md](12-TESTING_AND_QUALITY.md)*