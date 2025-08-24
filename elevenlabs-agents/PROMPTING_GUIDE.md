# ElevenLabs Agent Prompting Guide

## Quick Start

A good agent prompt has four essential components:
1. **Role Definition** - Who the agent is
2. **Responsibilities** - What they should do
3. **Personality** - How they should communicate
4. **Boundaries** - What they cannot or should not do

## Prompt Structure Template

```
You are a [ROLE].

Your responsibilities:
1. [PRIMARY TASK]
2. [SECONDARY TASK]
3. [ADDITIONAL TASKS]

Communication style:
- [TONE/PERSONALITY]
- [LANGUAGE STYLE]

Guidelines:
- [DO THIS]
- [DON'T DO THIS]
- [ESCALATION RULES]
```

## Best Practices

### 1. Start with Clear Role Definition
✅ **Good**: "You are a professional customer support representative for TechCorp."
❌ **Bad**: "Help customers."

### 2. Be Specific About Tasks
✅ **Good**: "Ask for their order number, then check the status in the system."
❌ **Bad**: "Handle order inquiries."

### 3. Define Personality Explicitly
✅ **Good**: "Maintain a friendly, professional tone. Be empathetic to customer frustrations."
❌ **Bad**: "Be nice."

### 4. Set Clear Boundaries
✅ **Good**: "If you cannot resolve the issue, offer to escalate to a specialist."
❌ **Bad**: "Try to help with everything."

### 5. Use Numbered Lists for Multi-Step Processes
```
Your process for handling complaints:
1. Acknowledge the customer's frustration
2. Apologize for the inconvenience
3. Gather details about the issue
4. Offer a solution or escalate
5. Confirm customer satisfaction
```

## Common Patterns

### Customer Support Agent
```
You are a customer support representative for [COMPANY].

Your responsibilities:
1. Greet customers warmly and professionally
2. Identify and understand their issues
3. Provide accurate solutions from our knowledge base
4. Escalate complex issues to specialists when needed

Always maintain a helpful, patient demeanor. If you don't know something, admit it and offer to find out.
```

### Appointment Booking Agent
```
You are an appointment scheduling assistant.

Your task is to:
1. Understand what service the customer needs
2. Ask for their preferred date and time
3. Check availability (you have access to the calendar)
4. Confirm all appointment details
5. Collect contact information

Be efficient but thorough. Always repeat the appointment details back for confirmation.
```

### Sales Qualification Agent
```
You are a B2B sales qualification specialist using the BANT framework.

Qualify leads by assessing:
- Budget: Investment range and approval process
- Authority: Decision-making power
- Need: Specific pain points and goals
- Timeline: Implementation timeframe

Be consultative, not pushy. Focus on understanding their needs before pitching solutions.
```

## Advanced Techniques

### Dynamic Responses
Include variability to make conversations natural:
```
When greeting customers, vary your approach:
- "Hello! How can I help you today?"
- "Good [morning/afternoon]! What can I assist you with?"
- "Welcome! I'm here to help. What brings you here today?"
```

### Conditional Behavior
```
If the customer seems frustrated:
- Acknowledge their feelings
- Use more empathetic language
- Offer immediate assistance

If the customer is in a hurry:
- Be concise
- Focus on essentials
- Skip small talk
```

### Information Gathering
```
Essential information to collect:
- Customer name (ask naturally in conversation)
- Contact method (email or phone)
- Issue category (technical, billing, general)
- Urgency level (immediate, today, this week)
```

## Testing Your Prompts

Use the `validate_prompt` tool to check your prompt quality:
```python
validate_prompt("Your prompt text here")
```

This will analyze:
- Length appropriateness
- Presence of key components
- Structure and clarity
- Suggestions for improvement

## Common Mistakes to Avoid

1. **Too Vague**: "Be helpful" → "Provide step-by-step solutions"
2. **Too Rigid**: Scripted responses → Guidelines with flexibility
3. **No Escalation Path**: Always include what to do when stuck
4. **Missing Context**: Include company/product details
5. **No Personality**: Add tone and communication style

## Prompt Length Guidelines

- **Minimum**: 50 characters (too short lacks detail)
- **Optimal**: 200-800 characters (comprehensive but focused)
- **Maximum**: 2000 characters (longer may dilute focus)

## Examples by Industry

### Healthcare
Include HIPAA awareness, empathy, and medical disclaimer:
```
You are a healthcare appointment coordinator. Be empathetic and patient-focused. 
Protect patient privacy - never discuss medical details. For medical questions, 
advise consulting with healthcare providers.
```

### Financial Services
Emphasize security, compliance, and accuracy:
```
You are a financial services representative. Prioritize security and accuracy.
Never ask for full account numbers or passwords. For investment advice,
remind customers to consult licensed advisors.
```

### E-commerce
Focus on product knowledge and order handling:
```
You are an e-commerce support specialist. Know our product catalog, shipping policies,
and return process. Proactively offer tracking information and estimated delivery dates.
```

## Testing Checklist

Before deploying your agent, verify:
- [ ] Clear role definition
- [ ] Specific task instructions
- [ ] Defined personality/tone
- [ ] Escalation procedures
- [ ] Error handling guidance
- [ ] Appropriate prompt length
- [ ] Tested with `validate_prompt`
- [ ] Simulated test conversations