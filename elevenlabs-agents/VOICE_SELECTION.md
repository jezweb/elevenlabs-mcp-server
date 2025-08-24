# Voice Selection Guide for ElevenLabs Agents

## Quick Selection Matrix

| Use Case | Recommended Preset | Stability | Speed | Style |
|----------|-------------------|-----------|-------|-------|
| Customer Support | Professional | 0.8 | 1.0 | 0.0 |
| Sales | Energetic | 0.3 | 1.1 | 0.4 |
| Healthcare | Calm | 0.9 | 0.95 | 0.0 |
| Booking/Scheduling | Friendly | 0.5 | 1.05 | 0.2 |
| Technical Support | Professional | 0.8 | 1.0 | 0.0 |
| Marketing/Social | Youthful | 0.4 | 1.08 | 0.3 |
| Legal/Financial | Authoritative | 0.85 | 0.98 | 0.1 |
| Surveys/Feedback | Friendly | 0.5 | 1.05 | 0.2 |

## Voice Parameters Explained

### Stability (0.0 - 1.0)
Controls voice consistency and emotional range.
- **0.0-0.3**: Very expressive, wide emotional range, varied delivery
- **0.4-0.6**: Balanced expression and consistency
- **0.7-1.0**: Very stable, consistent, minimal variation

### Similarity Boost (0.0 - 1.0)
How closely the voice adheres to its original training.
- **0.0-0.3**: Creative interpretation, more varied
- **0.4-0.7**: Natural variation while maintaining character
- **0.8-1.0**: Strict adherence to original voice

### Speed (0.7 - 1.2)
Speaking rate multiplier.
- **0.7-0.9**: Slower, more deliberate (good for complex info)
- **1.0**: Normal conversational speed
- **1.1-1.2**: Faster, energetic (good for enthusiasm)

### Style (0.0 - 1.0)
Amplifies the voice's stylistic characteristics.
- **0.0**: Neutral, no style amplification
- **0.1-0.3**: Subtle style enhancement
- **0.4-0.6**: Moderate style expression
- **0.7-1.0**: Strong style amplification (use sparingly)

## Preset Configurations

### Professional (Business/Corporate)
```json
{
  "voice_id": "cgSgspJ2msm6clMCkdW9",
  "stability": 0.8,
  "similarity_boost": 0.9,
  "speed": 1.0,
  "style": 0.0
}
```
**Use for**: Customer service, technical support, corporate reception

### Friendly (Casual/Approachable)
```json
{
  "voice_id": "21m00Tcm4TlvDq8ikWAM",
  "stability": 0.5,
  "similarity_boost": 0.7,
  "speed": 1.05,
  "style": 0.2
}
```
**Use for**: Appointment booking, surveys, order assistance

### Energetic (Sales/Marketing)
```json
{
  "voice_id": "yoZ06aMxZJJ28mfd3POQ",
  "stability": 0.3,
  "similarity_boost": 0.5,
  "speed": 1.1,
  "style": 0.4
}
```
**Use for**: Sales calls, product demos, lead generation

### Calm (Healthcare/Wellness)
```json
{
  "voice_id": "EXAVITQu4vr4xnSDxMaL",
  "stability": 0.9,
  "similarity_boost": 0.95,
  "speed": 0.95,
  "style": 0.0
}
```
**Use for**: Healthcare, counseling, meditation, crisis support

## Voice Selection by Industry

### Retail & E-commerce
- **Primary**: Friendly (warm, helpful)
- **Alternative**: Professional (for complaints)
- **Settings**: Medium stability, slightly faster speed

### Healthcare & Medical
- **Primary**: Calm (patient, reassuring)
- **Alternative**: Empathetic (for sensitive topics)
- **Settings**: High stability, slower speed

### Financial Services
- **Primary**: Authoritative (trustworthy, knowledgeable)
- **Alternative**: Professional (for general inquiries)
- **Settings**: High stability, normal speed

### Technology & SaaS
- **Primary**: Professional (clear, competent)
- **Alternative**: Youthful (for consumer products)
- **Settings**: Medium-high stability, normal speed

### Hospitality & Travel
- **Primary**: Friendly (welcoming, enthusiastic)
- **Alternative**: Efficient (for quick bookings)
- **Settings**: Medium stability, slightly faster speed

## Matching Voice to Brand Personality

### Luxury/Premium Brands
- Use **Authoritative** or **Professional**
- High stability (0.8-0.9)
- Normal to slightly slower speed
- Minimal style amplification

### Youth/Trendy Brands
- Use **Youthful** or **Energetic**
- Lower stability (0.3-0.5)
- Faster speed (1.05-1.1)
- Moderate style (0.3-0.4)

### Family/Community Brands
- Use **Friendly** or **Empathetic**
- Medium stability (0.5-0.6)
- Normal speed
- Light style (0.1-0.2)

### Technical/B2B Brands
- Use **Professional** or **Neutral**
- High stability (0.7-0.8)
- Normal speed
- No style amplification

## Cultural Considerations

### Regional Preferences
- **North America**: Friendly, enthusiastic
- **Europe**: Professional, reserved
- **Asia**: Polite, respectful
- **Latin America**: Warm, personal

### Age Demographics
- **Gen Z**: Youthful, expressive, faster
- **Millennials**: Friendly, conversational
- **Gen X**: Professional, efficient
- **Boomers**: Clear, patient, slower

## Testing Voice Selection

### Using the Tools

1. **Get voice suggestions**:
```python
suggest_voice_for_use_case("customer support for tech company")
```

2. **List available voices**:
```python
list_voices()
```

3. **Get preset details**:
```python
get_voice_preset("professional")
```

4. **Test configuration**:
```python
configure_voice(agent_id, voice_id, stability, similarity_boost, speed)
```

### A/B Testing Strategy

Test different voice configurations:
1. Create two identical agents with different voices
2. Run similar conversations through both
3. Compare customer satisfaction metrics
4. Adjust parameters based on results

## Common Voice Issues and Solutions

### Issue: Too Monotonous
- **Solution**: Decrease stability (0.3-0.5)
- Add slight style (0.1-0.2)

### Issue: Too Variable/Inconsistent
- **Solution**: Increase stability (0.7-0.9)
- Increase similarity boost (0.8-0.95)

### Issue: Too Fast/Overwhelming
- **Solution**: Reduce speed (0.9-0.95)
- Increase stability for clarity

### Issue: Lacks Energy
- **Solution**: Increase speed slightly (1.05-1.1)
- Decrease stability (0.4-0.5)
- Add style (0.2-0.3)

### Issue: Sounds Robotic
- **Solution**: Decrease similarity boost (0.5-0.7)
- Add minimal style (0.1)
- Vary stability (0.4-0.6)

## Performance Optimization

### For High-Volume Agents
- Use moderate settings to prevent listener fatigue
- Stability: 0.6-0.7
- Speed: 1.0
- Style: 0.0-0.1

### For Short Interactions
- Can use more expressive settings
- Stability: 0.3-0.5
- Speed: 1.05-1.1
- Style: 0.2-0.3

### For Long Conversations
- Prioritize clarity and consistency
- Stability: 0.7-0.8
- Speed: 0.95-1.0
- Style: 0.0

## Voice Customization Examples

### Example 1: Friendly Tech Support
```python
configure_voice(
    agent_id="agent_xxx",
    voice_id="21m00Tcm4TlvDq8ikWAM",
    stability="0.6",      # Balanced
    similarity_boost="0.75",  # Natural
    speed="1.0"           # Normal
)
```

### Example 2: Enthusiastic Sales
```python
configure_voice(
    agent_id="agent_yyy",
    voice_id="yoZ06aMxZJJ28mfd3POQ",
    stability="0.3",      # Expressive
    similarity_boost="0.5",   # Creative
    speed="1.1"           # Energetic
)
```

### Example 3: Calm Healthcare
```python
configure_voice(
    agent_id="agent_zzz",
    voice_id="EXAVITQu4vr4xnSDxMaL",
    stability="0.9",      # Very stable
    similarity_boost="0.95",  # Consistent
    speed="0.95"          # Slightly slower
)
```