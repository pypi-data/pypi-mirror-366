#!/usr/bin/env python3
"""
Google Calendar integration nodes for KayGraph.
Handles OAuth2, calendar operations, and event-driven workflows.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import os
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Node, AsyncNode, ValidatedNode, BatchNode

logger = logging.getLogger(__name__)


@dataclass
class CalendarEvent:
    """Represents a calendar event."""
    id: Optional[str] = None
    summary: str = ""
    description: Optional[str] = None
    start: datetime = None
    end: datetime = None
    location: Optional[str] = None
    attendees: List[str] = None
    reminders: List[Dict] = None
    calendar_id: str = "primary"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to Google Calendar API format."""
        event = {
            'summary': self.summary,
            'start': {
                'dateTime': self.start.isoformat() if self.start else datetime.now().isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': self.end.isoformat() if self.end else (datetime.now() + timedelta(hours=1)).isoformat(),
                'timeZone': 'UTC',
            }
        }
        
        if self.description:
            event['description'] = self.description
        if self.location:
            event['location'] = self.location
        if self.attendees:
            event['attendees'] = [{'email': email} for email in self.attendees]
        if self.reminders:
            event['reminders'] = {
                'useDefault': False,
                'overrides': self.reminders
            }
        
        return event


class OAuthNode(Node):
    """Handle Google OAuth2 authentication."""
    
    def __init__(self, 
                 credentials_file: str = "credentials.json",
                 token_file: str = "token.json",
                 scopes: Optional[List[str]] = None):
        super().__init__(node_id="oauth")
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.scopes = scopes or [
            'https://www.googleapis.com/auth/calendar.readonly',
            'https://www.googleapis.com/auth/calendar.events'
        ]
        self.creds = None
    
    def exec(self, _) -> Dict[str, Any]:
        """Authenticate with Google Calendar API."""
        logger.info("🔐 Authenticating with Google Calendar...")
        
        # In production, use real Google Auth libraries
        # from google.auth.transport.requests import Request
        # from google.oauth2.credentials import Credentials
        # from google_auth_oauthlib.flow import InstalledAppFlow
        
        # Mock authentication for demonstration
        if os.path.exists(self.token_file):
            logger.info("📄 Loading existing token...")
            # In production: creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
            self.creds = {"token": "mock_token", "valid": True}
        else:
            logger.info("🌐 Starting OAuth flow...")
            # In production: 
            # flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, self.scopes)
            # self.creds = flow.run_local_server(port=0)
            self.creds = {"token": "new_mock_token", "valid": True}
            
            # Save the credentials
            with open(self.token_file, 'w') as token:
                json.dump(self.creds, token)
        
        return {
            "authenticated": True,
            "scopes": self.scopes,
            "token_file": self.token_file
        }
    
    def post(self, shared: Dict[str, Any], prep_res, auth_result: Dict[str, Any]) -> None:
        """Store authentication credentials."""
        shared["google_creds"] = self.creds
        shared["authenticated"] = auth_result["authenticated"]
        logger.info("✅ Authentication successful")


class CalendarNode(ValidatedNode):
    """Core calendar operations node."""
    
    def __init__(self, operation: str = "list_events"):
        super().__init__(node_id=f"calendar_{operation}")
        self.operation = operation
    
    def validate_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate operation inputs."""
        if self.operation == "create_event":
            if "summary" not in data:
                raise ValueError("Event summary is required")
        elif self.operation == "delete_event":
            if "event_id" not in data:
                raise ValueError("Event ID is required")
        return data
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare calendar operation."""
        if not shared.get("authenticated"):
            raise RuntimeError("Not authenticated. Run OAuthNode first.")
        
        return {
            "creds": shared.get("google_creds"),
            "operation": self.operation,
            "params": shared.get("calendar_params", {})
        }
    
    def exec(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute calendar operation."""
        operation = context["operation"]
        params = context["params"]
        
        logger.info(f"📅 Executing calendar operation: {operation}")
        
        # In production, use real Google Calendar API
        # service = build('calendar', 'v3', credentials=context["creds"])
        
        if operation == "list_events":
            return self._list_events(params)
        elif operation == "create_event":
            return self._create_event(params)
        elif operation == "update_event":
            return self._update_event(params)
        elif operation == "delete_event":
            return self._delete_event(params)
        elif operation == "list_calendars":
            return self._list_calendars(params)
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def _list_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List calendar events."""
        calendar_id = params.get("calendar_id", "primary")
        time_min = params.get("time_min", datetime.now().isoformat() + 'Z')
        max_results = params.get("max_results", 10)
        
        # Mock response
        events = [
            {
                "id": "event1",
                "summary": "Team Meeting",
                "start": {"dateTime": "2024-03-15T10:00:00Z"},
                "end": {"dateTime": "2024-03-15T11:00:00Z"},
                "attendees": [{"email": "colleague@example.com"}]
            },
            {
                "id": "event2",
                "summary": "Project Review",
                "start": {"dateTime": "2024-03-15T14:00:00Z"},
                "end": {"dateTime": "2024-03-15T15:00:00Z"},
                "location": "Conference Room A"
            }
        ]
        
        return {
            "events": events,
            "calendar_id": calendar_id,
            "total": len(events)
        }
    
    def _create_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a calendar event."""
        event_data = params.get("event", {})
        calendar_id = params.get("calendar_id", "primary")
        
        # Create event object
        if isinstance(event_data, dict):
            event = CalendarEvent(**event_data)
        else:
            event = event_data
        
        # Mock creation
        event.id = f"event_{int(time.time())}"
        
        logger.info(f"✅ Created event: {event.summary}")
        
        return {
            "event_id": event.id,
            "summary": event.summary,
            "calendar_id": calendar_id,
            "created": True
        }
    
    def _update_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a calendar event."""
        event_id = params["event_id"]
        updates = params.get("updates", {})
        calendar_id = params.get("calendar_id", "primary")
        
        logger.info(f"📝 Updating event {event_id}")
        
        return {
            "event_id": event_id,
            "updated_fields": list(updates.keys()),
            "calendar_id": calendar_id,
            "updated": True
        }
    
    def _delete_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a calendar event."""
        event_id = params["event_id"]
        calendar_id = params.get("calendar_id", "primary")
        
        logger.info(f"🗑️ Deleting event {event_id}")
        
        return {
            "event_id": event_id,
            "calendar_id": calendar_id,
            "deleted": True
        }
    
    def _list_calendars(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available calendars."""
        # Mock calendar list
        calendars = [
            {"id": "primary", "summary": "Primary Calendar", "primary": True},
            {"id": "work@example.com", "summary": "Work Calendar"},
            {"id": "personal@example.com", "summary": "Personal Calendar"}
        ]
        
        return {
            "calendars": calendars,
            "total": len(calendars)
        }
    
    def post(self, shared: Dict[str, Any], context: Dict, result: Dict[str, Any]) -> None:
        """Store operation results."""
        shared[f"calendar_{self.operation}_result"] = result
        
        if self.operation == "list_events" and result.get("events"):
            shared["upcoming_events"] = result["events"]


class EventTriggerNode(AsyncNode):
    """Monitor calendar events and trigger workflows."""
    
    def __init__(self, 
                 trigger_patterns: Optional[List[str]] = None,
                 advance_minutes: int = 15):
        super().__init__(node_id="event_trigger")
        self.trigger_patterns = trigger_patterns or ["meeting", "sync", "review"]
        self.advance_minutes = advance_minutes
    
    async def prep_async(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get events to check for triggers."""
        return {
            "events": shared.get("upcoming_events", []),
            "current_time": datetime.now()
        }
    
    async def exec_async(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check events and identify triggers."""
        events = context["events"]
        current_time = context["current_time"]
        triggers = []
        
        for event in events:
            # Parse event time
            start_str = event.get("start", {}).get("dateTime", "")
            if not start_str:
                continue
            
            # Mock datetime parsing
            event_time = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            time_until = (event_time - current_time).total_seconds() / 60
            
            # Check if event should trigger
            if 0 <= time_until <= self.advance_minutes:
                # Check if event matches patterns
                summary = event.get("summary", "").lower()
                if any(pattern in summary for pattern in self.trigger_patterns):
                    triggers.append({
                        "event": event,
                        "trigger_time": current_time.isoformat(),
                        "minutes_until": time_until,
                        "matched_pattern": next(p for p in self.trigger_patterns if p in summary)
                    })
                    
                    logger.info(f"🔔 Trigger: {event['summary']} in {time_until:.0f} minutes")
        
        return triggers
    
    async def post_async(self, shared: Dict[str, Any], context: Dict, triggers: List[Dict]) -> str:
        """Store triggers and determine action."""
        shared["event_triggers"] = triggers
        
        if triggers:
            shared["triggered_events"] = [t["event"] for t in triggers]
            return "handle_triggers"
        else:
            return "no_triggers"


class ReminderNode(Node):
    """Handle event reminders and notifications."""
    
    def __init__(self, notification_methods: Optional[List[str]] = None):
        super().__init__(node_id="reminder")
        self.notification_methods = notification_methods or ["log", "email"]
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get events needing reminders."""
        return {
            "triggered_events": shared.get("triggered_events", []),
            "user_preferences": shared.get("reminder_preferences", {})
        }
    
    def exec(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Send reminders for events."""
        events = context["triggered_events"]
        notifications = []
        
        for event in events:
            summary = event.get("summary", "Event")
            start = event.get("start", {}).get("dateTime", "")
            location = event.get("location", "No location specified")
            
            for method in self.notification_methods:
                if method == "log":
                    logger.info(f"📢 Reminder: {summary} starting soon at {location}")
                    notification = {
                        "method": "log",
                        "status": "sent",
                        "event_id": event.get("id")
                    }
                elif method == "email":
                    # Mock email sending
                    notification = {
                        "method": "email",
                        "status": "queued",
                        "event_id": event.get("id"),
                        "recipient": "user@example.com",
                        "subject": f"Reminder: {summary}"
                    }
                    logger.info(f"📧 Email reminder queued for: {summary}")
                else:
                    notification = {
                        "method": method,
                        "status": "unsupported",
                        "event_id": event.get("id")
                    }
                
                notifications.append(notification)
        
        return notifications
    
    def post(self, shared: Dict[str, Any], context: Dict, notifications: List[Dict]) -> None:
        """Store notification results."""
        shared["reminder_notifications"] = notifications
        shared["reminders_sent"] = len([n for n in notifications if n["status"] in ["sent", "queued"]])


class CalendarSyncNode(BatchNode):
    """Sync events between calendars."""
    
    def __init__(self, source_calendar: str, target_calendar: str):
        super().__init__(node_id="calendar_sync")
        self.source_calendar = source_calendar
        self.target_calendar = target_calendar
    
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get events to sync."""
        # Get events from source calendar
        source_events = shared.get(f"{self.source_calendar}_events", [])
        
        # Filter events that need syncing
        events_to_sync = []
        for event in source_events:
            # Check if event should be synced (mock logic)
            if not event.get("private", False):
                events_to_sync.append({
                    "event": event,
                    "source": self.source_calendar,
                    "target": self.target_calendar
                })
        
        return events_to_sync
    
    def exec(self, sync_item: Dict[str, Any]) -> Dict[str, Any]:
        """Sync a single event."""
        event = sync_item["event"]
        target = sync_item["target"]
        
        # Mock syncing
        logger.info(f"🔄 Syncing '{event['summary']}' to {target}")
        
        return {
            "event_id": event.get("id"),
            "synced_to": target,
            "status": "success",
            "synced_id": f"{target}_{event.get('id')}"
        }
    
    def post(self, shared: Dict[str, Any], sync_items: List[Dict], results: List[Dict]) -> None:
        """Store sync results."""
        shared["sync_results"] = results
        shared["events_synced"] = len([r for r in results if r["status"] == "success"])
        
        logger.info(f"✅ Synced {shared['events_synced']} events")


class SmartSchedulerNode(Node):
    """AI-powered meeting scheduler."""
    
    def __init__(self):
        super().__init__(node_id="smart_scheduler")
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare scheduling context."""
        return {
            "attendees": shared.get("meeting_attendees", []),
            "duration": shared.get("meeting_duration", 60),  # minutes
            "preferences": shared.get("scheduling_preferences", {}),
            "existing_events": shared.get("upcoming_events", [])
        }
    
    def exec(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Find optimal meeting time."""
        attendees = context["attendees"]
        duration = context["duration"]
        existing_events = context["existing_events"]
        
        logger.info(f"🤖 Finding optimal time for {len(attendees)} attendees...")
        
        # Mock smart scheduling algorithm
        # In production, this would:
        # 1. Check each attendee's calendar
        # 2. Find common free slots
        # 3. Apply preferences (morning/afternoon, avoid lunch, etc.)
        # 4. Score slots based on multiple factors
        
        # Mock result
        suggested_times = [
            {
                "start": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
                "end": (datetime.now() + timedelta(days=1, hours=2, minutes=duration)).isoformat(),
                "score": 0.95,
                "conflicts": [],
                "reason": "All attendees free, preferred morning slot"
            },
            {
                "start": (datetime.now() + timedelta(days=2, hours=6)).isoformat(),
                "end": (datetime.now() + timedelta(days=2, hours=6, minutes=duration)).isoformat(),
                "score": 0.82,
                "conflicts": [],
                "reason": "All attendees free, afternoon slot"
            }
        ]
        
        return {
            "suggested_times": suggested_times,
            "best_time": suggested_times[0] if suggested_times else None,
            "attendees_checked": len(attendees)
        }
    
    def post(self, shared: Dict[str, Any], context: Dict, result: Dict[str, Any]) -> None:
        """Store scheduling results."""
        shared["scheduling_suggestions"] = result["suggested_times"]
        shared["optimal_meeting_time"] = result["best_time"]
        
        if result["best_time"]:
            logger.info(f"📍 Best meeting time: {result['best_time']['start']}")


if __name__ == "__main__":
    # Test calendar nodes
    import asyncio
    
    # Test OAuth
    oauth = OAuthNode()
    shared = {}
    oauth.run(shared)
    
    # Test calendar operations
    if shared.get("authenticated"):
        # List events
        list_node = CalendarNode(operation="list_events")
        list_node.run(shared)
        
        # Check for triggers
        trigger = EventTriggerNode()
        asyncio.run(trigger.run_async(shared))
        
        # Send reminders if triggered
        if shared.get("triggered_events"):
            reminder = ReminderNode()
            reminder.run(shared)
    
    print(f"\nCalendar integration test completed!")
    print(f"Events found: {len(shared.get('upcoming_events', []))}")
    print(f"Triggers: {len(shared.get('event_triggers', []))}")
    print(f"Reminders sent: {shared.get('reminders_sent', 0)}")