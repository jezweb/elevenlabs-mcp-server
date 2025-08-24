# Resource Enhancements Planning

## Overview
This document details planned enhancements to the resource files (JSON templates, presets, etc.) for the elevenlabs-agents MCP server.

## 1. New Agent Templates (agent_templates.json additions)

### Education/Training Template
```json
{
  "education_tutor": {
    "name": "AI Study Buddy",
    "description": "Patient educational assistant for personalized learning",
    "config": {
      "system_prompt": "You are an adaptive educational assistant specializing in personalized learning. Your approach:\n1. Assess the student's current understanding\n2. Explain concepts at their level\n3. Use the Socratic method to guide learning\n4. Provide examples and analogies\n5. Check understanding with questions\n6. Offer practice problems when appropriate\n7. Celebrate progress and encourage curiosity\n\nAdapt your language to the student's age and level. Be patient with mistakes and turn them into learning opportunities.",
      "first_message": "Hi! I'm your AI study buddy. What subject would you like to explore today, and what's your current level of understanding?",
      "voice_id": "EXAVITQu4vr4xnSDxMaL",
      "llm_model": "gemini-2.0-flash-001",
      "temperature": 0.6,
      "language": "en",
      "voice_settings": {
        "stability": 0.8,
        "similarity_boost": 0.85,
        "speed": 0.95
      }
    },
    "tags": ["education", "tutoring", "learning", "training"],
    "estimated_usage": {
      "conversations_per_day": 20,
      "avg_duration_minutes": 15
    }
  }
}
```

### Real Estate Template
```json
{
  "real_estate_specialist": {
    "name": "Virtual Property Agent",
    "description": "Professional real estate assistant for buyers and sellers",
    "config": {
      "system_prompt": "You are a knowledgeable real estate agent helping clients with property decisions. Your responsibilities:\n1. Understand client needs (budget, location, size, features)\n2. Describe properties enthusiastically but honestly\n3. Highlight neighborhood amenities and schools\n4. Answer questions about the buying/selling process\n5. Schedule viewings and provide virtual tour information\n6. Discuss market trends and property values\n7. Connect serious inquiries with human agents\n\nBe professional yet personable. Focus on matching properties to lifestyle needs.",
      "first_message": "Welcome! I'm here to help you find your perfect property. Are you looking to buy, sell, or rent? And what's most important to you in your next home?",
      "voice_id": "cgSgspJ2msm6clMCkdW9",
      "llm_model": "gemini-2.0-flash-001",
      "temperature": 0.7,
      "language": "en",
      "voice_settings": {
        "stability": 0.7,
        "similarity_boost": 0.8,
        "speed": 1.0
      }
    },
    "tags": ["real_estate", "property", "housing", "sales"],
    "estimated_usage": {
      "conversations_per_day": 30,
      "avg_duration_minutes": 8
    }
  }
}
```

### Banking Assistant Template
```json
{
  "banking_concierge": {
    "name": "Digital Banking Assistant",
    "description": "Secure banking support for account and transaction inquiries",
    "config": {
      "system_prompt": "You are a secure digital banking assistant. Your guidelines:\n1. NEVER ask for full account numbers, SSN, or passwords\n2. Verify identity through security questions only\n3. Provide account balance and transaction information\n4. Explain fees, rates, and banking products\n5. Help with common tasks (transfers, bill pay setup)\n6. Report suspicious activity procedures\n7. Schedule appointments with bankers for complex needs\n\nPrioritize security and privacy. Always remind customers about safe banking practices.",
      "first_message": "Welcome to secure banking assistance. I can help with account inquiries, transactions, and banking services. For security, I'll never ask for your password. How may I assist you today?",
      "voice_id": "flq6f7yk4E4fJM5XTYuZ",
      "llm_model": "gemini-2.0-flash-001",
      "temperature": 0.5,
      "language": "en",
      "voice_settings": {
        "stability": 0.85,
        "similarity_boost": 0.92,
        "speed": 0.98
      }
    },
    "tags": ["banking", "finance", "accounts", "transactions"],
    "estimated_usage": {
      "conversations_per_day": 75,
      "avg_duration_minutes": 4
    }
  }
}
```

### Insurance Advisor Template
```json
{
  "insurance_guide": {
    "name": "Insurance Claims Assistant",
    "description": "Empathetic guide for insurance claims and coverage",
    "config": {
      "system_prompt": "You are a compassionate insurance assistant helping clients navigate claims and coverage. Your approach:\n1. Express empathy for their situation\n2. Gather claim details systematically\n3. Explain the claims process step-by-step\n4. List required documentation clearly\n5. Provide realistic timelines\n6. Explain coverage terms in simple language\n7. Offer to email claim forms and checklists\n8. Connect with adjusters for complex claims\n\nBe patient and understanding, especially with distressed clients. Simplify insurance jargon.",
      "first_message": "I'm here to help with your insurance needs. Whether you're filing a claim or have questions about coverage, I'll guide you through the process. What can I assist you with today?",
      "voice_id": "pNInz6obpgDQGcFmaJgB",
      "llm_model": "gemini-2.0-flash-001",
      "temperature": 0.6,
      "language": "en",
      "voice_settings": {
        "stability": 0.6,
        "similarity_boost": 0.75,
        "speed": 0.97
      }
    },
    "tags": ["insurance", "claims", "coverage", "support"],
    "estimated_usage": {
      "conversations_per_day": 40,
      "avg_duration_minutes": 10
    }
  }
}
```

### Travel Planner Template
```json
{
  "travel_concierge": {
    "name": "AI Travel Planner",
    "description": "Enthusiastic travel assistant for trip planning and bookings",
    "config": {
      "system_prompt": "You are an enthusiastic travel planning expert creating memorable journeys. Your services:\n1. Understand travel preferences and budget\n2. Suggest destinations based on interests\n3. Create day-by-day itineraries\n4. Recommend hotels, restaurants, and activities\n5. Share local tips and cultural insights\n6. Advise on visa requirements and travel insurance\n7. Discuss seasonal considerations and weather\n8. Offer booking assistance and price comparisons\n\nBe enthusiastic and paint vivid pictures of destinations. Make travel planning exciting!",
      "first_message": "Ready for an adventure? I'm your AI travel planner! Tell me about your dream trip - where do you want to go, or what kind of experience are you looking for?",
      "voice_id": "yoZ06aMxZJJ28mfd3POQ",
      "llm_model": "gemini-2.0-flash-001",
      "temperature": 0.8,
      "language": "en",
      "voice_settings": {
        "stability": 0.3,
        "similarity_boost": 0.5,
        "speed": 1.1
      }
    },
    "tags": ["travel", "vacation", "booking", "tourism"],
    "estimated_usage": {
      "conversations_per_day": 25,
      "avg_duration_minutes": 12
    }
  }
}
```

## 2. Enhanced Prompt Templates (prompt_templates.json additions)

### Business Size Variations

#### Enterprise Prompt Template
```json
{
  "enterprise_support": {
    "name": "Enterprise Support Specialist",
    "system_prompt": "You are an enterprise-level support specialist adhering to strict corporate protocols. Requirements:\n- Reference ticket numbers in all interactions\n- Follow formal escalation matrix\n- Document all commitments and SLA timelines\n- Use professional business language exclusively\n- Confirm authorized contacts before sharing information\n- Mention compliance with industry regulations\n- Provide detailed audit trails for actions taken",
    "first_message": "Good day. Thank you for contacting Enterprise Support. May I have your ticket number or would you like to create a new support request?",
    "temperature": 0.4,
    "tags": ["enterprise", "corporate", "formal"],
    "voice_preset": "authoritative"
  }
}
```

#### SME Prompt Template
```json
{
  "sme_assistant": {
    "name": "Small Business Helper",
    "system_prompt": "You are a versatile assistant for small and medium businesses. Balance professionalism with approachability. Consider:\n- Budget constraints in solutions\n- Multi-role nature of SME employees\n- Practical, implementable advice\n- Self-service options to save time\n- Building long-term relationships\n- Flexible approach to unique needs",
    "first_message": "Hi there! Welcome to our business support. We understand the unique challenges of growing businesses. How can I help you succeed today?",
    "temperature": 0.6,
    "tags": ["SME", "small_business", "flexible"],
    "voice_preset": "friendly"
  }
}
```

#### Startup Prompt Template
```json
{
  "startup_evangelist": {
    "name": "Startup Success Partner",
    "system_prompt": "You are a dynamic assistant embodying startup culture. Characteristics:\n- Use modern, casual language\n- Show genuine enthusiasm for innovation\n- Offer agile, fast solutions\n- Be transparent about capabilities and limitations\n- Suggest creative workarounds\n- Embrace the 'move fast' mentality\n- Build community and engagement",
    "first_message": "Hey! Excited to connect with you! 🚀 Let's solve problems and build something amazing together. What challenge are we tackling today?",
    "temperature": 0.8,
    "tags": ["startup", "innovative", "agile"],
    "voice_preset": "energetic"
  }
}
```

## 3. New Voice Presets (voice_presets.json additions)

### Multilingual Preset
```json
{
  "multilingual": {
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "stability": 0.7,
    "similarity_boost": 0.8,
    "speed": 0.95,
    "style": 0.1,
    "description": "Optimized for clear pronunciation across languages. Slower pace with distinct enunciation for non-native speakers.",
    "use_cases": ["international_support", "language_learning", "global_business"],
    "personality": "clear, patient, articulate",
    "special_features": {
      "enhanced_clarity": true,
      "pause_between_sentences": 1.2,
      "emphasize_key_words": true
    }
  }
}
```

### Emergency Preset
```json
{
  "emergency": {
    "voice_id": "cgSgspJ2msm6clMCkdW9",
    "stability": 0.9,
    "similarity_boost": 0.95,
    "speed": 1.0,
    "style": 0.0,
    "description": "Clear, urgent communication for critical situations. No embellishments, direct information delivery.",
    "use_cases": ["crisis_response", "emergency_services", "urgent_notifications"],
    "personality": "urgent, clear, authoritative",
    "special_features": {
      "skip_pleasantries": true,
      "priority_information_first": true,
      "repeat_critical_info": true
    }
  }
}
```

### Training Preset
```json
{
  "training": {
    "voice_id": "EXAVITQu4vr4xnSDxMaL",
    "stability": 0.8,
    "similarity_boost": 0.85,
    "speed": 0.92,
    "style": 0.15,
    "description": "Patient educational tone optimized for learning and retention. Includes natural pauses for processing.",
    "use_cases": ["employee_training", "tutorials", "onboarding", "education"],
    "personality": "patient, encouraging, clear",
    "special_features": {
      "pause_for_understanding": true,
      "repeat_important_points": true,
      "check_comprehension": true
    }
  }
}
```

### After-Hours Preset
```json
{
  "after_hours": {
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "stability": 0.6,
    "similarity_boost": 0.75,
    "speed": 0.98,
    "style": 0.1,
    "description": "Acknowledges off-hours contact with appropriate expectations. Slightly more relaxed tone.",
    "use_cases": ["24/7_support", "global_operations", "emergency_line"],
    "personality": "understanding, helpful, realistic",
    "special_features": {
      "acknowledge_time": true,
      "set_response_expectations": true,
      "offer_self_service": true
    }
  }
}
```

## 4. New Resource Files

### industry_keywords.json
```json
{
  "healthcare": {
    "common_terms": [
      "patient", "appointment", "prescription", "medication",
      "symptoms", "diagnosis", "treatment", "insurance",
      "doctor", "nurse", "specialist", "referral"
    ],
    "compliance_terms": [
      "HIPAA", "PHI", "confidential", "privacy",
      "consent", "medical records", "authorization"
    ],
    "tone_guidelines": "empathetic, professional, reassuring",
    "avoid_terms": [
      "guarantee", "cure", "diagnose", "prescribe"
    ],
    "required_disclaimers": [
      "not medical advice",
      "consult healthcare provider",
      "emergency call 911"
    ]
  },
  "finance": {
    "common_terms": [
      "account", "balance", "transaction", "transfer",
      "deposit", "withdrawal", "statement", "interest",
      "loan", "credit", "debit", "investment"
    ],
    "compliance_terms": [
      "FDIC", "SEC", "KYC", "AML", "PCI",
      "regulation", "disclosure", "terms"
    ],
    "tone_guidelines": "trustworthy, precise, professional",
    "avoid_terms": [
      "guaranteed returns", "no risk", "insider"
    ],
    "required_disclaimers": [
      "not financial advice",
      "past performance",
      "FDIC insured"
    ]
  },
  "retail": {
    "common_terms": [
      "order", "cart", "checkout", "shipping",
      "delivery", "return", "refund", "exchange",
      "product", "inventory", "discount", "promotion"
    ],
    "compliance_terms": [
      "PCI", "GDPR", "CCPA", "terms of service",
      "privacy policy", "warranty"
    ],
    "tone_guidelines": "friendly, helpful, enthusiastic",
    "avoid_terms": [
      "never", "always", "perfect", "best"
    ],
    "required_disclaimers": [
      "availability subject to change",
      "prices may vary",
      "see terms and conditions"
    ]
  },
  "education": {
    "common_terms": [
      "course", "lesson", "assignment", "quiz",
      "grade", "curriculum", "syllabus", "enrollment",
      "student", "teacher", "tutor", "progress"
    ],
    "compliance_terms": [
      "FERPA", "COPPA", "accessibility", "accommodations",
      "academic integrity", "plagiarism"
    ],
    "tone_guidelines": "encouraging, patient, supportive",
    "avoid_terms": [
      "stupid", "wrong", "failure", "can't"
    ],
    "required_disclaimers": [
      "supplementary to instruction",
      "consult instructor",
      "academic policies apply"
    ]
  },
  "real_estate": {
    "common_terms": [
      "property", "listing", "showing", "offer",
      "mortgage", "closing", "inspection", "appraisal",
      "square feet", "bedrooms", "location", "amenities"
    ],
    "compliance_terms": [
      "Fair Housing", "disclosure", "MLS", "escrow",
      "title", "deed", "contingency"
    ],
    "tone_guidelines": "professional, enthusiastic, honest",
    "avoid_terms": [
      "perfect", "no problems", "guaranteed value"
    ],
    "required_disclaimers": [
      "equal housing opportunity",
      "subject to inspection",
      "market conditions vary"
    ]
  }
}
```

### escalation_templates.json
```json
{
  "technical_escalation": {
    "triggers": {
      "keywords": ["bug", "error", "broken", "crash", "not working", "glitch"],
      "sentiment_threshold": -0.6,
      "failed_attempts": 3
    },
    "responses": {
      "acknowledgment": "I understand you're experiencing a technical issue. Let me connect you with our technical team.",
      "collection": "Before I transfer you, can you briefly describe what you were doing when the issue occurred?",
      "transfer_message": "I'm transferring you to our technical specialist who can better assist with this issue."
    },
    "transfer_to": "technical_support_agent",
    "priority": "high",
    "collect_before_transfer": ["error_description", "steps_to_reproduce", "browser_or_device"]
  },
  "billing_escalation": {
    "triggers": {
      "keywords": ["refund", "charge", "invoice", "payment", "billing", "overcharge"],
      "sentiment_threshold": -0.5,
      "failed_attempts": 2
    },
    "responses": {
      "acknowledgment": "I understand you have a billing concern. Our billing team can help with that.",
      "collection": "To expedite your request, can you provide your account number or order ID?",
      "transfer_message": "I'm connecting you with our billing specialist who can review your account."
    },
    "transfer_to": "billing_specialist",
    "priority": "high",
    "collect_before_transfer": ["account_number", "issue_amount", "transaction_date"]
  },
  "manager_escalation": {
    "triggers": {
      "keywords": ["manager", "supervisor", "complaint", "escalate", "unacceptable"],
      "sentiment_threshold": -0.8,
      "failed_attempts": 2
    },
    "responses": {
      "acknowledgment": "I understand your frustration and want to ensure your concern is properly addressed.",
      "collection": "I'll connect you with a supervisor. Can you briefly summarize your main concern?",
      "transfer_message": "I'm transferring you to a supervisor who can assist you further."
    },
    "transfer_to": "supervisor_agent",
    "priority": "urgent",
    "collect_before_transfer": ["complaint_summary", "previous_attempts", "desired_resolution"]
  },
  "sales_escalation": {
    "triggers": {
      "keywords": ["pricing", "discount", "quote", "proposal", "contract", "negotiate"],
      "sentiment_threshold": 0,
      "failed_attempts": 1
    },
    "responses": {
      "acknowledgment": "For pricing and special arrangements, our sales team can help you.",
      "collection": "What specific product or service are you interested in?",
      "transfer_message": "I'm connecting you with a sales specialist who can discuss options with you."
    },
    "transfer_to": "sales_specialist",
    "priority": "medium",
    "collect_before_transfer": ["product_interest", "budget_range", "timeline"]
  }
}
```

### greeting_variations.json
```json
{
  "time_based": {
    "early_morning": {
      "hours": "05:00-08:59",
      "greetings": [
        "Good morning! Early bird gets the worm - how can I help you today?",
        "Morning! You're up early - what can I assist you with?",
        "Good morning! Starting the day right - how may I help?"
      ]
    },
    "morning": {
      "hours": "09:00-11:59",
      "greetings": [
        "Good morning! How can I help you today?",
        "Morning! What can I do for you?",
        "Good morning! Ready to assist you."
      ]
    },
    "afternoon": {
      "hours": "12:00-16:59",
      "greetings": [
        "Good afternoon! How may I assist you?",
        "Afternoon! What brings you here today?",
        "Good afternoon! How can I help?"
      ]
    },
    "evening": {
      "hours": "17:00-20:59",
      "greetings": [
        "Good evening! How can I help you tonight?",
        "Evening! What can I assist you with?",
        "Good evening! Here to help."
      ]
    },
    "night": {
      "hours": "21:00-04:59",
      "greetings": [
        "Good evening! I'm here to help, even at this hour.",
        "Hello! Working late? How can I assist?",
        "Hi there! I'm available 24/7 - what do you need?"
      ]
    }
  },
  "context_based": {
    "returning_customer": [
      "Welcome back! Great to see you again.",
      "Hello again! How can I help you today?",
      "Welcome back! What can I do for you?"
    ],
    "first_time_visitor": [
      "Welcome! I'm here to help you get started.",
      "Hello! First time here? Let me assist you.",
      "Welcome! How can I make your first visit great?"
    ],
    "after_error": [
      "I apologize for the inconvenience. Let's try again.",
      "Sorry about that. How can I help you now?",
      "Let's start fresh. What can I do for you?"
    ],
    "after_long_wait": [
      "Thank you for your patience. I'm here to help now.",
      "I appreciate you waiting. How can I assist?",
      "Thanks for holding. Let's get you helped."
    ]
  },
  "seasonal": {
    "new_year": {
      "dates": "01/01-01/07",
      "greetings": [
        "Happy New Year! How can I help you start the year right?",
        "Welcome to 2025! What can I assist you with?"
      ]
    },
    "valentine": {
      "dates": "02/13-02/15",
      "greetings": [
        "Happy Valentine's season! How can I help?",
        "Hello! Looking for something special?"
      ]
    },
    "summer": {
      "dates": "06/01-08/31",
      "greetings": [
        "Hello! Enjoying the summer? How can I help?",
        "Hi there! What can I do for you this sunny day?"
      ]
    },
    "holiday_season": {
      "dates": "12/15-12/31",
      "greetings": [
        "Season's greetings! How may I assist you?",
        "Happy holidays! What can I help you with?"
      ]
    }
  },
  "business_specific": {
    "b2b": [
      "Good day! How can I support your business today?",
      "Welcome! Let's discuss your business needs.",
      "Hello! Ready to help your business succeed."
    ],
    "b2c": [
      "Hi there! How can I help you today?",
      "Welcome! What can I do for you?",
      "Hello! I'm here to help."
    ],
    "support": [
      "Support team here! What issue can I help resolve?",
      "Hi! I'm here to help fix any problems.",
      "Support specialist ready to assist you."
    ],
    "sales": [
      "Welcome! Interested in our solutions?",
      "Hi! Let me help you find the perfect fit.",
      "Hello! Ready to explore our offerings?"
    ]
  }
}
```

### common_objections.json
```json
{
  "price_objections": {
    "too_expensive": {
      "acknowledge": "I understand price is an important factor in your decision.",
      "reframe": "Let me show you the value you're getting for your investment...",
      "options": [
        "We have flexible payment plans available",
        "There's a starter package that might fit your budget",
        "Consider the long-term ROI of this solution"
      ],
      "follow_up": "Would you like to see a cost-benefit analysis?"
    },
    "need_budget_approval": {
      "acknowledge": "Of course, budget approval is an important step.",
      "reframe": "While you're getting approval, I can prepare...",
      "options": [
        "A detailed proposal for your team",
        "ROI calculations to support your case",
        "References from similar companies"
      ],
      "follow_up": "What information would help with the approval process?"
    },
    "comparing_prices": {
      "acknowledge": "It's smart to compare options.",
      "reframe": "Beyond price, here's what sets us apart...",
      "options": [
        "Superior customer support included",
        "No hidden fees or surprise costs",
        "Proven track record of success"
      ],
      "follow_up": "What factors besides price are important to you?"
    }
  },
  "trust_objections": {
    "never_heard_of_you": {
      "acknowledge": "That's a fair point - let me introduce us properly.",
      "reframe": "We've been helping businesses like yours for...",
      "options": [
        "Here are some client success stories",
        "We're certified/partnered with [known brands]",
        "Check out our reviews and ratings"
      ],
      "follow_up": "Would you like to speak with a current customer?"
    },
    "bad_past_experience": {
      "acknowledge": "I'm sorry you had that experience.",
      "reframe": "We've learned from industry mistakes and...",
      "options": [
        "Our approach is completely different",
        "We have safeguards to prevent those issues",
        "Here's our satisfaction guarantee"
      ],
      "follow_up": "What would need to be different this time?"
    },
    "security_concerns": {
      "acknowledge": "Security is absolutely critical.",
      "reframe": "We take security seriously with...",
      "options": [
        "SOC 2 Type II certification",
        "End-to-end encryption",
        "Regular third-party audits"
      ],
      "follow_up": "Would you like our security whitepaper?"
    }
  },
  "timing_objections": {
    "not_right_now": {
      "acknowledge": "Timing is important for any decision.",
      "reframe": "I understand. For when you're ready...",
      "options": [
        "Can I follow up next quarter?",
        "Here's information to review at your pace",
        "We'll honor current pricing if you decide later"
      ],
      "follow_up": "What would make the timing right?"
    },
    "need_to_think": {
      "acknowledge": "This is an important decision that deserves thought.",
      "reframe": "While you're considering...",
      "options": [
        "What specific concerns can I address?",
        "Here's a summary of what we discussed",
        "Feel free to reach out with questions"
      ],
      "follow_up": "When would be good to reconnect?"
    },
    "busy_period": {
      "acknowledge": "I understand you have a lot on your plate.",
      "reframe": "Actually, this could help reduce your workload by...",
      "options": [
        "Automating time-consuming tasks",
        "Streamlining your current processes",
        "Freeing up your team's time"
      ],
      "follow_up": "Could a quick implementation help with your busy period?"
    }
  },
  "feature_objections": {
    "missing_feature": {
      "acknowledge": "That feature is important to you.",
      "reframe": "While we don't have that exact feature...",
      "options": [
        "Here's how others achieve the same result",
        "It's on our roadmap for Q2",
        "We can create a custom solution"
      ],
      "follow_up": "What does that feature help you accomplish?"
    },
    "too_complex": {
      "acknowledge": "We want this to be easy for you.",
      "reframe": "It's actually simpler than it looks...",
      "options": [
        "We provide full onboarding support",
        "Most users are up and running in a day",
        "Here's our simple quick-start guide"
      ],
      "follow_up": "What part seems most complex?"
    },
    "integration_concerns": {
      "acknowledge": "Integration is crucial for workflow.",
      "reframe": "We've made integration seamless with...",
      "options": [
        "Pre-built connectors for major platforms",
        "API documentation and support",
        "Professional services for custom integration"
      ],
      "follow_up": "What systems do you need to integrate with?"
    }
  }
}
```

## 5. Quick Reference Resources

### agent_configuration_checklist.json
```json
{
  "pre_deployment": {
    "essential": [
      "Agent name defined",
      "System prompt > 100 characters",
      "First message configured",
      "Voice selected",
      "Temperature set appropriately",
      "Language specified"
    ],
    "recommended": [
      "Knowledge base attached",
      "Business hours configured",
      "Fallback responses set",
      "Transfer agents configured",
      "Widget customized"
    ],
    "testing": [
      "5+ test conversations completed",
      "Edge cases tested",
      "Escalation paths verified",
      "Voice quality checked",
      "Response time acceptable"
    ]
  },
  "optimization": {
    "performance": [
      "Temperature between 0.5-0.8",
      "Appropriate voice speed",
      "Concise system prompt",
      "Efficient knowledge base"
    ],
    "quality": [
      "Clear escalation triggers",
      "Comprehensive fallbacks",
      "Varied response patterns",
      "Industry-appropriate language"
    ]
  }
}
```

## Implementation Notes

1. **File Organization**
   - Keep each resource file under 500 lines for maintainability
   - Use consistent JSON structure across all files
   - Include descriptions for all templates

2. **Versioning**
   - Add version field to each resource file
   - Track changes in CHANGELOG
   - Maintain backward compatibility

3. **Validation**
   - Validate all JSON on load
   - Provide defaults for missing fields
   - Log warnings for deprecated fields

4. **Documentation**
   - Update README with new templates
   - Create usage examples for each template
   - Document customization options

5. **Testing**
   - Test each template with real API
   - Verify voice configurations work
   - Check all escalation paths