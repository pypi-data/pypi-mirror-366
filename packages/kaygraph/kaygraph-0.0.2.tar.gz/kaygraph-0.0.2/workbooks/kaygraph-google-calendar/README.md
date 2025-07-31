# KayGraph Google Calendar Integration

This example demonstrates how to integrate Google Calendar with KayGraph workflows, enabling calendar-driven automation and event management.

## Features

1. **OAuth2 Authentication**: Secure Google account connection
2. **Event Management**: Create, read, update, delete calendar events
3. **Event Triggers**: Start workflows based on calendar events
4. **Reminder Handling**: Automated reminders and notifications
5. **Multi-Calendar Support**: Work with multiple calendars

## Setup

### 1. Google Cloud Setup
```bash
# 1. Go to https://console.cloud.google.com
# 2. Create a new project or select existing
# 3. Enable Google Calendar API
# 4. Create OAuth2 credentials
# 5. Download credentials.json
```

### 2. Install Dependencies
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 3. First Run
```bash
# Authenticate (opens browser)
python main.py --auth

# Test connection
python main.py --list-calendars
```

## Usage

### Basic Operations
```bash
# List upcoming events
python main.py --list-events

# Create an event
python main.py --create-event "Team Meeting" --date "2024-03-15" --time "14:00"

# Search events
python main.py --search "project review"

# Delete event
python main.py --delete-event EVENT_ID
```

### Workflow Integration
```bash
# Run workflow triggered by calendar events
python main.py --workflow meeting-prep

# Schedule workflow execution
python main.py --schedule-workflow "daily-standup" --time "09:00"

# Event-driven automation
python main.py --auto-respond --calendar "work"
```

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   OAuth2 Node   │────▶│  Calendar Node  │────▶│  Trigger Node   │
│ (Authenticate)  │     │ (Read/Write)    │     │ (Start Workflow)│
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │  Event Handler  │
                        │ (Process Events)│
                        └─────────────────┘
```

## Key Components

### 1. OAuthNode
Handles Google OAuth2 authentication flow:
- Manages credentials
- Refreshes tokens
- Stores auth state

### 2. CalendarNode
Core calendar operations:
- List calendars
- CRUD operations on events
- Query and filter events

### 3. EventTriggerNode
Workflow triggering based on events:
- Monitor calendar changes
- Match event patterns
- Start appropriate workflows

### 4. ReminderNode
Handle event reminders:
- Email notifications
- SMS alerts
- In-app notifications

## Example Workflows

### 1. Meeting Preparation
```python
# Automatically prepare for meetings
- Detect upcoming meetings
- Gather related documents
- Send prep materials to attendees
- Create meeting notes template
```

### 2. Task Scheduling
```python
# Convert calendar events to tasks
- Read events with specific tags
- Create corresponding tasks
- Update task status
- Sync back to calendar
```

### 3. Availability Management
```python
# Manage availability across calendars
- Check multiple calendars
- Find free slots
- Block time automatically
- Send availability to requesters
```

## Configuration

Create `config.json`:
```json
{
  "google": {
    "credentials_file": "credentials.json",
    "token_file": "token.json",
    "scopes": [
      "https://www.googleapis.com/auth/calendar.readonly",
      "https://www.googleapis.com/auth/calendar.events"
    ]
  },
  "calendars": {
    "primary": "primary",
    "work": "work@company.com",
    "personal": "personal@gmail.com"
  },
  "triggers": {
    "meeting_prep": {
      "pattern": "meeting|sync|call",
      "advance_minutes": 15
    },
    "daily_summary": {
      "time": "08:00",
      "calendars": ["primary", "work"]
    }
  }
}
```

## Security Considerations

1. **Credential Storage**: Never commit credentials to git
2. **Scope Limitation**: Request only needed permissions
3. **Token Refresh**: Handle token expiration gracefully
4. **Access Control**: Validate calendar access rights
5. **Data Privacy**: Handle calendar data securely

## Error Handling

The integration handles:
- Network failures
- Authentication errors
- Rate limiting
- Invalid event data
- Calendar permission issues

## Advanced Features

### 1. Batch Operations
```python
# Process multiple events efficiently
batch_node = BatchCalendarNode()
events = batch_node.create_recurring_events(pattern)
```

### 2. Calendar Sync
```python
# Sync between multiple calendars
sync_node = CalendarSyncNode(source="work", target="personal")
sync_node.sync_events(filter={"type": "meeting"})
```

### 3. Smart Scheduling
```python
# AI-powered scheduling
scheduler = SmartSchedulerNode()
best_time = scheduler.find_optimal_meeting_time(attendees, duration)
```

## Troubleshooting

- **Auth Issues**: Delete token.json and re-authenticate
- **API Limits**: Implement exponential backoff
- **Sync Conflicts**: Use event IDs for deduplication
- **Missing Events**: Check calendar permissions