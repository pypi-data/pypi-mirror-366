# KayGraph Chat with Guardrails

A specialized chatbot that only responds to specific topics (travel-related) and politely redirects off-topic questions, demonstrating content filtering and safety controls.

## What it does

This travel assistant chatbot:
- **Topic Filtering**: Only responds to travel-related queries
- **Content Moderation**: Checks for safety and appropriateness
- **Polite Redirects**: Guides users back to supported topics
- **Input Validation**: Sanitizes and validates user input
- **Response Filtering**: Ensures safe, appropriate outputs

## Features

### Guardrail Types

1. **Topic Guardrails**
   - Classifies queries into travel categories
   - Detects off-topic requests
   - Provides confidence scores

2. **Safety Guardrails**
   - Blocks harmful content
   - Flags sensitive topics
   - Requires disclaimers when needed

3. **Input Validation**
   - Length limits
   - Script injection prevention
   - Empty input handling

4. **Response Filtering**
   - Removes sensitive information
   - Ensures appropriate formatting
   - Adds necessary disclaimers

## How to run

```bash
python main.py
```

## Architecture

```
InputValidationNode → TopicClassificationNode
                              ↓ (on_topic)      ↓ (off_topic)
                      ContentModerationNode   OffTopicRedirectNode
                         ↓ safe  ↓ unsafe              ↓
                 OnTopicResponseNode SafetyResponseNode
                              ↓            ↓           ↓
                           ResponseFilterNode
```

### Node Descriptions

1. **InputValidationNode**: Validates and sanitizes user input
2. **TopicClassificationNode**: Classifies query into travel topics
3. **ContentModerationNode**: Checks content safety
4. **OnTopicResponseNode**: Generates travel-related responses
5. **OffTopicRedirectNode**: Creates polite redirects
6. **SafetyResponseNode**: Handles unsafe content
7. **ResponseFilterNode**: Final filtering and formatting

## Supported Topics

The chatbot specializes in:
- ✈️ **Destinations**: Places to visit, recommendations
- 📅 **Planning**: Itineraries, scheduling, preparation
- 🚗 **Transportation**: Flights, trains, car rentals
- 🏨 **Accommodation**: Hotels, hostels, vacation rentals
- 🎯 **Activities**: Things to do, attractions, experiences
- 💰 **Budget**: Costs, saving tips, budget planning
- 🛡️ **Safety**: Travel safety, health precautions
- 📄 **Documents**: Passports, visas, requirements
- 🎒 **Packing**: What to bring, luggage tips
- ☀️ **Weather**: Climate, best times to visit
- 🌍 **Culture**: Local customs, etiquette
- 🍽️ **Food**: Local cuisine, restaurants

## Example Interactions

### On-Topic Query
```
You: What are the best beaches in Thailand?

[Debug - Topic: destinations, On-topic: True]

🤖 Travel Assistant: Great question about travel destinations! Based on your interest in 'What are the best beaches in Thailand?', I can help you explore amazing places to visit, from tropical beaches to mountain adventures.

🌟 Happy travels! Feel free to ask more travel questions!
```

### Off-Topic Query
```
You: How do I learn Python programming?

[Debug - Topic: other, On-topic: False]

🤖 Travel Assistant: I notice you're asking about other, but I'm specifically trained for travel topics. How about I help you plan an exciting trip instead?

✈️ Here are some travel topics I can help with:
• Finding the perfect destination
• Travel planning and itineraries
• Budget travel tips
• Transportation options
• Accommodation recommendations

🌟 Happy travels! Feel free to ask more travel questions!
```

### Safety-Flagged Query
```
You: Tell me about travel medical insurance

[Debug - Topic: safety, On-topic: True]

🤖 Travel Assistant: ⚕️ Health Notice: While I can share general travel health tips, please consult healthcare professionals for medical advice specific to your travel plans.

Regarding your travel question about 'Tell me about travel medical insurance', here's what I can share...

🌟 Happy travels! Feel free to ask more travel questions!
```

## Customization

### Adding New Topics
Modify `TRAVEL_TOPICS` in `utils/guardrails.py`:
```python
TRAVEL_TOPICS = [
    "destinations",
    "planning",
    # Add new topics here
    "photography",  # Travel photography
    "solo_travel",  # Solo travel tips
]
```

### Adjusting Safety Rules
Update `SAFETY_RULES`:
```python
SAFETY_RULES = {
    "blocked_terms": ["violence", "illegal"],
    "sensitive_topics": ["politics", "medical_advice"],
    "max_length": 1000
}
```

### Custom Responses
Modify response generation in `OnTopicResponseNode` to add:
- Dynamic responses based on LLM
- Database of travel information
- Integration with travel APIs

## Use Cases

- **Customer Service**: Travel agency chatbots
- **Travel Planning**: Vacation planning assistants
- **Tourism Websites**: Destination information bots
- **Travel Apps**: In-app travel advisors
- **Educational**: Travel safety training

## Best Practices

1. **Clear Communication**: Always explain the bot's specialization
2. **Helpful Redirects**: Guide users to supported topics
3. **Safety First**: Err on the side of caution with content
4. **Transparency**: Show when content is filtered or moderated
5. **User Education**: Help users understand what's supported

Perfect for building specialized, safe chatbots!