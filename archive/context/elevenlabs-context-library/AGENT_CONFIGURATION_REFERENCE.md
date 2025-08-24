# ElevenLabs Agent Configuration Reference
*Complete Guide to All Configuration Options*

## Table of Contents
1. [LLM Configuration](#llm-configuration)
2. [Voice Configuration](#voice-configuration)
3. [Audio Settings](#audio-settings)
4. [Conversation Settings](#conversation-settings)
5. [Privacy & Retention](#privacy--retention)
6. [Client Events](#client-events)
7. [Keywords & Recognition](#keywords--recognition)
8. [Pronunciation Dictionaries](#pronunciation-dictionaries)
9. [Agent Languages](#agent-languages)
10. [SDK vs Embed Configuration](#sdk-vs-embed-configuration)

---

## LLM Configuration

### Available Models

#### Gemini Models (Google)
| Model | Best For | Speed | Cost | Max Context |
|-------|----------|-------|------|-------------|
| `gemini-2.5-flash-lite` | Simple routing, pattern matching | Fastest | Lowest | 8K tokens |
| `gemini-2.5-flash` | General purpose, data collection | Fast | Low | 32K tokens |
| `gemini-2.5-pro` | Complex reasoning, technical accuracy | Moderate | Higher | 128K tokens |
| `gemini-2.0-flash` | Latest general purpose | Fast | Low | 32K tokens |

#### OpenAI Models
| Model | Best For | Speed | Cost | Max Context |
|-------|----------|-------|------|-------------|
| `gpt-4o-mini` | Reliable tool calling, structured output | Fast | Low | 16K tokens |
| `gpt-4o` | Complex reasoning, nuanced conversation | Moderate | High | 128K tokens |
| `gpt-4-turbo` | Maximum capability | Slower | Highest | 128K tokens |

#### Claude Models (Anthropic)
| Model | Best For | Speed | Cost | Max Context |
|-------|----------|-------|------|-------------|
| `claude-3-haiku` | Fast responses, simple tasks | Fastest | Lowest | 200K tokens |
| `claude-3-sonnet` | Balanced performance | Fast | Moderate | 200K tokens |
| `claude-3-opus` | Maximum intelligence | Slower | Highest | 200K tokens |

### Temperature Configuration

```json
{
  "temperature": 0.4,  // 0.0 to 1.0
  "top_p": 0.9,       // 0.0 to 1.0
  "frequency_penalty": 0.1,  // -2.0 to 2.0
  "presence_penalty": 0.1,   // -2.0 to 2.0
  "max_tokens": 250   // Model-specific limits
}
```

#### Temperature by Use Case

**Ultra-Low (0.0-0.2)**
- Compliance statements
- Legal disclaimers
- Emergency protocols
- Exact routing rules

**Low (0.2-0.3)**
- Simple routing
- Pattern matching
- Standard responses
- Technical accuracy

**Medium-Low (0.3-0.4)**
- Information delivery
- FAQ responses
- Service descriptions
- Pricing information

**Medium (0.4-0.5)**
- General conversation
- Data collection
- Customer service
- Booking processes

**Medium-High (0.5-0.6)**
- Sales conversations
- Persuasive content
- Relationship building
- Consultative dialogue

**High (0.6-0.7)**
- Creative storytelling
- Entertainment
- Personality-driven chat
- Dynamic engagement

**Ultra-High (0.7-1.0)**
- Maximum creativity
- Unpredictable responses
- Experimental use only

### Advanced LLM Parameters

#### Top P (Nucleus Sampling)
Controls diversity of word choices
- **0.9**: Standard, good balance
- **0.85**: More focused responses
- **0.95**: More diverse vocabulary
- **1.0**: Consider all options

#### Frequency Penalty
Reduces repetition of words/phrases
- **0.0**: No penalty (may repeat)
- **0.1-0.3**: Slight reduction in repetition
- **0.4-0.6**: Moderate variety enforcement
- **0.7-1.0**: Strong variety (may sound unnatural)

#### Presence Penalty
Encourages discussing new topics
- **0.0**: No penalty
- **0.1-0.3**: Slight topic variety
- **0.4-0.6**: Moderate topic shifting
- **0.7-1.0**: Constantly new topics

#### Max Tokens
Controls response length
- **50-100**: Very short (routing, confirmations)
- **100-200**: Short (simple answers)
- **200-300**: Medium (explanations)
- **300-500**: Long (detailed technical)
- **500+**: Very long (comprehensive)

---

## Voice Configuration

### Voice Settings Deep Dive

```json
{
  "voice_id": "XrExE9yKIg1WjnnlVkGX",
  "model_id": "eleven_turbo_v2",
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.8,
    "style": 0.4,
    "use_speaker_boost": true
  }
}
```

#### Stability (0.0 - 1.0)
Controls consistency vs expressiveness
- **0.0-0.3**: Maximum variation, emotional range
- **0.3-0.5**: Natural variation, expressive
- **0.5-0.7**: Balanced consistency
- **0.7-0.9**: Very consistent, professional
- **0.9-1.0**: Robotic consistency

#### Similarity Boost (0.0 - 1.0)
How closely to match original voice
- **0.0-0.5**: Loose interpretation
- **0.5-0.7**: Moderate matching
- **0.7-0.9**: Close matching (recommended)
- **0.9-1.0**: Exact matching attempt

#### Style (0.0 - 1.0)
Amplifies voice characteristics
- **0.0**: No style enhancement
- **0.1-0.3**: Subtle enhancement
- **0.4-0.6**: Moderate style
- **0.7-1.0**: Strong style (may affect quality)

#### Speaker Boost
- **true**: Enhanced clarity, better in noisy environments
- **false**: Natural sound, lower processing

### Voice Model Selection

| Model | Latency | Quality | Languages | Best For |
|-------|---------|---------|-----------|----------|
| `eleven_turbo_v2` | Lowest | Good | English | Real-time conversation |
| `eleven_turbo_v2_5` | Low | Better | 32 languages | Multilingual, balanced |
| `eleven_flash_v2` | Very Low | Good | English | Ultra-fast response |
| `eleven_flash_v2_5` | Very Low | Better | 32 languages | Fast multilingual |
| `eleven_multilingual_v2` | Moderate | Best | 29 languages | Quality priority |
| `eleven_monolingual_v1` | Moderate | Good | English | Legacy compatibility |

---

## Audio Settings

### Input Audio Configuration

```json
{
  "user_input_audio_format": "pcm_16000",
  "input_sensitivity": 0.5,
  "noise_suppression": true,
  "echo_cancellation": true,
  "auto_gain_control": true
}
```

#### Audio Format Options

**PCM 16000 Hz (Recommended)**
```json
{
  "format": "pcm_16000",
  "benefits": [
    "Optimal for speech (80-8000 Hz range)",
    "Lower latency than higher rates",
    "4x less bandwidth than 48kHz",
    "Industry telephony standard",
    "Best real-time performance"
  ]
}
```

**PCM 8000 Hz**
```json
{
  "format": "pcm_8000",
  "use_cases": [
    "Very low bandwidth",
    "Phone quality acceptable",
    "Legacy system compatibility"
  ],
  "drawbacks": [
    "May miss high-frequency consonants",
    "Lower quality overall"
  ]
}
```

**PCM 48000 Hz**
```json
{
  "format": "pcm_48000",
  "use_cases": [
    "Music or mixed content",
    "Highest quality recording",
    "Professional audio needs"
  ],
  "drawbacks": [
    "Higher latency",
    "More bandwidth required",
    "Overkill for speech"
  ]
}
```

**μ-law 8000 Hz**
```json
{
  "format": "ulaw_8000",
  "use_cases": [
    "Twilio integration",
    "Traditional telephony",
    "Compressed transmission"
  ]
}
```

### Output Audio Configuration

```json
{
  "output_format": "mp3_44100_128",
  "streaming_mode": true,
  "buffer_size": 2048,
  "optimize_streaming_latency": 3
}
```

#### Output Format Options

| Format | Quality | Latency | Bandwidth | Use Case |
|--------|---------|---------|-----------|----------|
| `mp3_22050_32` | Low | Lowest | Minimal | Low bandwidth |
| `mp3_44100_64` | Medium | Low | Low | Standard web |
| `mp3_44100_128` | Good | Low | Moderate | Recommended |
| `mp3_44100_192` | High | Moderate | High | Premium tier |
| `pcm_16000` | Raw | Lowest | High | Processing |
| `pcm_44100` | Raw HD | Low | Very High | Pro tier |
| `opus_48000_64` | Good | Low | Low | Modern codec |

#### Optimize Streaming Latency

- **0**: No optimization (highest quality)
- **1**: Minimal optimization
- **2**: Balanced optimization
- **3**: Good optimization (recommended)
- **4**: Maximum optimization (may affect quality)

---

## Conversation Settings

### Turn Management

```json
{
  "turn_timeout": 60,
  "turn_timeout_message": "Are you still there?",
  "silence_detection_threshold": 0.5,
  "interruption_sensitivity": 0.5,
  "backchannel_frequency": "medium"
}
```

#### Turn Timeout Settings

| Setting | Value | Use Case |
|---------|-------|----------|
| Very Short | 10-20s | Quick routing, emergency |
| Short | 20-30s | Fast-paced conversation |
| Medium | 30-45s | Standard interaction |
| Long | 45-60s | Complex discussion |
| Very Long | 60-90s | Technical consultation |
| Infinite | -1 | Never timeout |

#### Silence End Call Timeout

```json
{
  "silence_end_call_timeout": -1,  // seconds or -1 for never
  "silence_threshold_db": -40,     // decibels
  "consecutive_silence_limit": 3   // number of silent turns
}
```

Recommended Settings:
- **Customer Service**: -1 (never auto-end)
- **Quick Info**: 30 seconds
- **Emergency**: -1 (never auto-end)
- **Entertainment**: 60 seconds

### Max Conversation Duration

```json
{
  "max_conversation_duration": 600,  // seconds
  "warning_before_end": 60,         // warn 1 minute before
  "hard_cutoff": false              // graceful vs immediate
}
```

Duration by Agent Type:
- **Router**: 180-300 seconds (3-5 min)
- **Information**: 300-600 seconds (5-10 min)
- **Booking**: 600-900 seconds (10-15 min)
- **Technical**: 900-1800 seconds (15-30 min)
- **Sales**: 1200-2400 seconds (20-40 min)

---

## Privacy & Retention

### Data Storage Configuration

```json
{
  "privacy_settings": {
    "store_conversation_audio": true,
    "store_transcripts": true,
    "store_metadata": true,
    "retention_period_days": 730,
    "delete_after_retention": true,
    "anonymize_pii": true
  }
}
```

#### Retention Period Options

| Period | Days | Use Case |
|--------|------|----------|
| Temporary | 1-7 | Testing only |
| Short | 30 | Minimal compliance |
| Medium | 90 | Standard operation |
| Long | 365 | Annual analysis |
| Extended | 730 | Full compliance |
| Permanent | -1 | Never delete |

#### PII Handling

```json
{
  "pii_detection": {
    "enabled": true,
    "types": [
      "phone_numbers",
      "email_addresses",
      "credit_cards",
      "social_security",
      "addresses",
      "names"
    ],
    "action": "redact",  // redact, encrypt, or flag
    "store_original": false
  }
}
```

### Compliance Settings

```json
{
  "compliance": {
    "gdpr_compliant": true,
    "ccpa_compliant": true,
    "hipaa_compliant": false,
    "data_residency": "australia",
    "encryption_at_rest": true,
    "encryption_in_transit": true
  }
}
```

---

## Client Events

### Event Configuration

```json
{
  "client_events": {
    "audio": true,              // Always required
    "interruption": true,       // User interrupts agent
    "user_transcript": true,    // User speech text
    "agent_response": true,     // Agent speech text
    "agent_response_correction": true,  // Agent corrections
    "agent_tool_response": true,  // IMPORTANT: Tool usage
    "vad_score": false,         // Voice activity score
    "latency_measurement": false,  // Performance metrics
    "emotion_detection": false    // Experimental
  }
}
```

### Event Details

#### Essential Events (Always Enable)
- **audio**: Raw audio stream
- **interruption**: Interruption detection
- **user_transcript**: User's spoken text
- **agent_response**: Agent's response text

#### Important Events (Recommended)
- **agent_response_correction**: Self-corrections
- **agent_tool_response**: Tool execution tracking

#### Debug Events (As Needed)
- **vad_score**: Voice activity detection scores
- **latency_measurement**: Latency metrics
- **network_stats**: Connection quality

#### Advanced Events
- **emotion_detection**: Sentiment analysis
- **language_switch**: Language changes
- **background_noise**: Noise levels

---

## Keywords & Recognition

### Keywords Configuration

```json
{
  "keywords": {
    "boost_phrases": [
      "company specific terms",
      "product names",
      "technical jargon",
      "local place names"
    ],
    "weight": 1.5,  // 1.0 to 2.0
    "case_sensitive": false
  }
}
```

### Industry-Specific Keywords

#### Medical/Healthcare
```json
[
  "symptoms", "diagnosis", "medication", "prescription",
  "appointment", "referral", "insurance", "copay",
  "emergency", "urgent care", "specialist"
]
```

#### Technical/IT
```json
[
  "API", "webhook", "database", "server", "cloud",
  "authentication", "encryption", "latency", "bandwidth",
  "deployment", "integration", "debugging"
]
```

#### E-commerce
```json
[
  "checkout", "cart", "shipping", "returns", "refund",
  "discount", "coupon", "inventory", "backorder",
  "tracking", "delivery", "payment"
]
```

#### Financial
```json
[
  "account", "balance", "transaction", "transfer",
  "deposit", "withdrawal", "interest", "loan",
  "credit", "debit", "statement"
]
```

---

## Pronunciation Dictionaries

### PLS File Format

```xml
<?xml version="1.0" encoding="UTF-8"?>
<lexicon version="1.0" 
         xmlns="http://www.w3.org/2005/01/pronunciation-lexicon"
         alphabet="ipa" 
         xml:lang="en-US">
  
  <!-- Company Names -->
  <lexeme>
    <grapheme>ElevenLabs</grapheme>
    <phoneme>ɪˈlɛvən læbz</phoneme>
  </lexeme>
  
  <!-- Technical Terms -->
  <lexeme>
    <grapheme>API</grapheme>
    <phoneme>eɪ piː aɪ</phoneme>
  </lexeme>
  
  <!-- Acronyms -->
  <lexeme>
    <grapheme>FAQ</grapheme>
    <phoneme>ɛf eɪ kjuː</phoneme>
  </lexeme>
  
  <!-- Names -->
  <lexeme>
    <grapheme>Nguyen</grapheme>
    <phoneme>ŋwɪn</phoneme>
  </lexeme>
</lexicon>
```

### Common IPA Patterns

#### Acronym Pronunciation
- Single letters: Spell out (API → eɪ piː aɪ)
- Pronounceable: As word (NASA → næsə)
- Mixed: Context dependent

#### Number Pronunciation
```xml
<lexeme>
  <grapheme>24/7</grapheme>
  <phoneme>twɛnti fɔr sɛvən</phoneme>
</lexeme>
```

---

## Agent Languages

### Multi-Language Configuration

```json
{
  "language_settings": {
    "default_language": "en-US",
    "additional_languages": [
      "es-ES",
      "fr-FR",
      "de-DE",
      "zh-CN"
    ],
    "auto_detect": true,
    "detection_confidence": 0.7,
    "fallback_language": "en-US"
  }
}
```

### Language Codes

#### Major Languages
| Code | Language | Region |
|------|----------|--------|
| en-US | English | United States |
| en-GB | English | United Kingdom |
| en-AU | English | Australia |
| es-ES | Spanish | Spain |
| es-MX | Spanish | Mexico |
| fr-FR | French | France |
| de-DE | German | Germany |
| it-IT | Italian | Italy |
| pt-BR | Portuguese | Brazil |
| zh-CN | Chinese | Simplified |
| ja-JP | Japanese | Japan |
| ko-KR | Korean | South Korea |

### Language-Specific Settings

```json
{
  "language_overrides": {
    "zh-CN": {
      "speaking_rate": 0.9,
      "pause_duration": 1.2
    },
    "es-ES": {
      "formality": "informal",
      "regional_variant": "castilian"
    }
  }
}
```

---

## SDK vs Embed Configuration

### Simple Embed

```html
<!-- Basic Embed -->
<elevenlabs-convai agent-id="agent_abc123"></elevenlabs-convai>
<script src="https://unpkg.com/@elevenlabs/convai-widget-embed" 
        async type="text/javascript"></script>
```

**Limitations:**
- No custom variables
- Limited styling options
- No event callbacks
- Basic configuration only

### SDK Implementation

```javascript
// Advanced SDK Configuration
const agent = await ElevenLabsConvai.create({
  agentId: 'agent_abc123',
  
  // Custom Variables
  variables: {
    business_name: 'ACME Corp',
    business_hours_start: '09:00',
    business_hours_end: '17:00',
    timezone: 'America/New_York'
  },
  
  // Audio Configuration
  audio: {
    input: {
      format: 'pcm_16000',
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true
    },
    output: {
      format: 'mp3_44100_128',
      volume: 0.8
    }
  },
  
  // Event Handlers
  onConnect: () => console.log('Connected'),
  onDisconnect: () => console.log('Disconnected'),
  onMessage: (msg) => console.log('Message:', msg),
  onError: (err) => console.error('Error:', err),
  
  // UI Configuration
  ui: {
    theme: 'dark',
    position: 'bottom-right',
    size: 'medium',
    colors: {
      primary: '#007bff',
      background: '#ffffff',
      text: '#333333'
    }
  },
  
  // Advanced Options
  startMinimized: false,
  autoConnect: true,
  reconnectAttempts: 3,
  connectionTimeout: 30000
});

// Register Client Tools
agent.registerTool('share_screen', async (params) => {
  // Implementation
  return { success: true };
});

// Start Conversation
await agent.start();
```

### Configuration Comparison

| Feature | Simple Embed | SDK |
|---------|-------------|-----|
| Setup Complexity | ⭐ | ⭐⭐⭐ |
| Custom Variables | ❌ | ✅ |
| Event Handlers | ❌ | ✅ |
| Client Tools | ❌ | ✅ |
| Custom Styling | Limited | Full |
| Dynamic Updates | ❌ | ✅ |
| Error Handling | Basic | Advanced |
| Analytics | Basic | Full |

---

## Configuration Templates

### Minimal Configuration
```json
{
  "agent_id": "agent_123",
  "llm": {
    "model": "gemini-2.5-flash-lite",
    "temperature": 0.3
  },
  "voice": {
    "voice_id": "default",
    "stability": 0.5
  }
}
```

### Standard Configuration
```json
{
  "agent_id": "agent_123",
  "llm": {
    "model": "gemini-2.5-flash",
    "temperature": 0.4,
    "max_tokens": 250,
    "top_p": 0.9
  },
  "voice": {
    "voice_id": "professional_voice",
    "stability": 0.5,
    "similarity_boost": 0.8,
    "style": 0.4,
    "use_speaker_boost": true
  },
  "audio": {
    "input_format": "pcm_16000",
    "output_format": "mp3_44100_128"
  },
  "conversation": {
    "turn_timeout": 60,
    "max_duration": 600
  }
}
```

### Advanced Configuration
```json
{
  "agent_id": "agent_123",
  "llm": {
    "model": "gemini-2.5-pro",
    "temperature": 0.3,
    "max_tokens": 400,
    "top_p": 0.85,
    "frequency_penalty": 0.1,
    "presence_penalty": 0.1
  },
  "voice": {
    "voice_id": "custom_cloned_voice",
    "model_id": "eleven_multilingual_v2",
    "stability": 0.6,
    "similarity_boost": 0.85,
    "style": 0.3,
    "use_speaker_boost": true
  },
  "audio": {
    "input_format": "pcm_16000",
    "output_format": "mp3_44100_192",
    "optimize_streaming_latency": 3,
    "noise_suppression": true,
    "echo_cancellation": true
  },
  "conversation": {
    "turn_timeout": 60,
    "silence_end_call_timeout": -1,
    "max_duration": 1800,
    "interruption_sensitivity": 0.5
  },
  "privacy": {
    "store_audio": true,
    "retention_days": 730,
    "anonymize_pii": true
  },
  "languages": {
    "default": "en-US",
    "additional": ["es-ES", "fr-FR"],
    "auto_detect": true
  },
  "client_events": {
    "audio": true,
    "interruption": true,
    "user_transcript": true,
    "agent_response": true,
    "agent_tool_response": true,
    "vad_score": true
  }
}
```

---

*Last Updated: 2025-08-15*
*Version: 2.0*
*Maintainer: jeremy@jezweb.net*