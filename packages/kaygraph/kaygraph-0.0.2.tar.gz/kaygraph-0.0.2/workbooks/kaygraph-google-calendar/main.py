#!/usr/bin/env python3
"""
Main example for Google Calendar integration with KayGraph.
"""

import argparse
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Graph, AsyncGraph
from calendar_nodes import (
    OAuthNode, CalendarNode, EventTriggerNode, 
    ReminderNode, CalendarSyncNode, SmartSchedulerNode,
    CalendarEvent
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def build_auth_workflow():
    """Build authentication workflow."""
    oauth = OAuthNode()
    verify = CalendarNode(operation="list_calendars")
    
    graph = Graph(start=oauth)
    oauth >> verify
    
    return graph


def build_event_management_workflow():
    """Build event creation and management workflow."""
    oauth = OAuthNode()
    create = CalendarNode(operation="create_event")
    list_events = CalendarNode(operation="list_events")
    
    graph = Graph(start=oauth)
    oauth >> create >> list_events
    
    return graph


def build_meeting_prep_workflow():
    """Build meeting preparation workflow."""
    oauth = OAuthNode()
    list_events = CalendarNode(operation="list_events")
    trigger = EventTriggerNode(
        trigger_patterns=["meeting", "sync", "call", "review"],
        advance_minutes=15
    )
    reminder = ReminderNode(notification_methods=["log", "email"])
    
    graph = AsyncGraph(start=oauth)
    oauth >> list_events >> trigger
    trigger - "handle_triggers" >> reminder
    
    return graph


def build_smart_scheduling_workflow():
    """Build AI-powered scheduling workflow."""
    oauth = OAuthNode()
    list_events = CalendarNode(operation="list_events")
    scheduler = SmartSchedulerNode()
    create = CalendarNode(operation="create_event")
    
    graph = Graph(start=oauth)
    oauth >> list_events >> scheduler >> create
    
    return graph


def build_calendar_sync_workflow():
    """Build calendar synchronization workflow."""
    oauth = OAuthNode()
    
    # List events from both calendars
    list_work = CalendarNode(operation="list_events")
    list_personal = CalendarNode(operation="list_events")
    
    # Sync from work to personal
    sync = CalendarSyncNode(
        source_calendar="work",
        target_calendar="personal"
    )
    
    graph = Graph(start=oauth)
    oauth >> list_work >> list_personal >> sync
    
    return graph


def run_list_events(args):
    """List upcoming events."""
    graph = Graph(start=OAuthNode())
    oauth = graph.start_node
    list_node = CalendarNode(operation="list_events")
    oauth >> list_node
    
    shared = {
        "calendar_params": {
            "calendar_id": args.calendar,
            "max_results": args.max_results
        }
    }
    
    graph.run(shared)
    
    events = shared.get("upcoming_events", [])
    print(f"\n📅 Upcoming Events ({len(events)} found):")
    print("="*60)
    
    for event in events:
        start = event.get("start", {}).get("dateTime", "No time")
        summary = event.get("summary", "No title")
        location = event.get("location", "")
        
        print(f"\n🗓️  {summary}")
        print(f"   Time: {start}")
        if location:
            print(f"   Location: {location}")
        
        attendees = event.get("attendees", [])
        if attendees:
            print(f"   Attendees: {', '.join(a['email'] for a in attendees)}")


def run_create_event(args):
    """Create a new event."""
    # Parse date and time
    event_datetime = datetime.strptime(f"{args.date} {args.time}", "%Y-%m-%d %H:%M")
    end_datetime = event_datetime + timedelta(hours=args.duration)
    
    # Create event
    event = CalendarEvent(
        summary=args.title,
        description=args.description,
        start=event_datetime,
        end=end_datetime,
        location=args.location,
        attendees=args.attendees.split(",") if args.attendees else None
    )
    
    # Build workflow
    graph = build_event_management_workflow()
    
    shared = {
        "calendar_params": {
            "calendar_id": args.calendar,
            "event": event.to_dict()
        }
    }
    
    graph.run(shared)
    
    result = shared.get("calendar_create_event_result", {})
    if result.get("created"):
        print(f"\n✅ Event created successfully!")
        print(f"   ID: {result['event_id']}")
        print(f"   Title: {result['summary']}")
        print(f"   Calendar: {result['calendar_id']}")


def run_meeting_prep(args):
    """Run meeting preparation workflow."""
    import asyncio
    
    graph = build_meeting_prep_workflow()
    
    shared = {
        "calendar_params": {
            "calendar_id": args.calendar,
            "time_min": datetime.now().isoformat() + 'Z',
            "max_results": 20
        },
        "reminder_preferences": {
            "advance_notice": args.advance_minutes
        }
    }
    
    asyncio.run(graph.run_async(shared))
    
    triggers = shared.get("event_triggers", [])
    if triggers:
        print(f"\n🔔 Meeting Preparation Triggers ({len(triggers)} found):")
        print("="*60)
        
        for trigger in triggers:
            event = trigger["event"]
            print(f"\n📅 {event['summary']}")
            print(f"   Starting in: {trigger['minutes_until']:.0f} minutes")
            print(f"   Matched pattern: {trigger['matched_pattern']}")
        
        reminders = shared.get("reminders_sent", 0)
        print(f"\n📢 Sent {reminders} reminders")
    else:
        print("\n✨ No upcoming meetings requiring preparation")


def run_smart_scheduling(args):
    """Run smart scheduling workflow."""
    graph = build_smart_scheduling_workflow()
    
    shared = {
        "meeting_attendees": args.attendees.split(","),
        "meeting_duration": args.duration * 60,  # Convert to minutes
        "scheduling_preferences": {
            "preferred_times": args.preferred_times,
            "avoid_lunch": True,
            "timezone": "UTC"
        }
    }
    
    graph.run(shared)
    
    suggestions = shared.get("scheduling_suggestions", [])
    if suggestions:
        print(f"\n🤖 Smart Scheduling Suggestions:")
        print("="*60)
        
        for i, slot in enumerate(suggestions[:3]):
            print(f"\n{i+1}. Score: {slot['score']:.2f}")
            print(f"   Start: {slot['start']}")
            print(f"   End: {slot['end']}")
            print(f"   Reason: {slot['reason']}")
        
        best = shared.get("optimal_meeting_time")
        if best:
            print(f"\n⭐ Recommended time: {best['start']}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="KayGraph Google Calendar Integration"
    )
    
    # Global options
    parser.add_argument(
        "--calendar",
        default="primary",
        help="Calendar ID to use"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Auth command
    auth_parser = subparsers.add_parser("auth", help="Authenticate with Google")
    
    # List events
    list_parser = subparsers.add_parser("list", help="List upcoming events")
    list_parser.add_argument("--max-results", type=int, default=10)
    
    # Create event
    create_parser = subparsers.add_parser("create", help="Create an event")
    create_parser.add_argument("title", help="Event title")
    create_parser.add_argument("--date", required=True, help="Date (YYYY-MM-DD)")
    create_parser.add_argument("--time", required=True, help="Time (HH:MM)")
    create_parser.add_argument("--duration", type=float, default=1.0, help="Duration in hours")
    create_parser.add_argument("--description", help="Event description")
    create_parser.add_argument("--location", help="Event location")
    create_parser.add_argument("--attendees", help="Comma-separated emails")
    
    # Meeting prep
    prep_parser = subparsers.add_parser("prep", help="Prepare for upcoming meetings")
    prep_parser.add_argument("--advance-minutes", type=int, default=15)
    
    # Smart scheduling
    schedule_parser = subparsers.add_parser("schedule", help="Find optimal meeting time")
    schedule_parser.add_argument("--attendees", required=True, help="Comma-separated emails")
    schedule_parser.add_argument("--duration", type=float, default=1.0, help="Duration in hours")
    schedule_parser.add_argument("--preferred-times", default="morning", choices=["morning", "afternoon", "evening"])
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    if args.command == "auth":
        graph = build_auth_workflow()
        shared = {}
        graph.run(shared)
        
        calendars = shared.get("calendar_list_calendars_result", {}).get("calendars", [])
        print(f"\n✅ Authenticated successfully!")
        print(f"📅 Found {len(calendars)} calendars:")
        for cal in calendars:
            print(f"   - {cal['summary']} ({cal['id']})")
    
    elif args.command == "list":
        run_list_events(args)
    
    elif args.command == "create":
        run_create_event(args)
    
    elif args.command == "prep":
        run_meeting_prep(args)
    
    elif args.command == "schedule":
        run_smart_scheduling(args)


if __name__ == "__main__":
    main()