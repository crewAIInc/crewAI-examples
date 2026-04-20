from crewai import Agent


class CalendarAgents:
    def temporal_analyst(self, tools):
        return Agent(
            role="Temporal Analyst",
            backstory=(
                "You are a time-awareness specialist. Before any calendar "
                "operation, you call get_temporal_context to learn the current "
                "time, timezone, UTC offset, and DST status. You convert "
                "natural language like 'next Tuesday at 2pm' into exact "
                "timestamps using resolve_datetime. You never guess dates "
                "or times — you always use the tools."
            ),
            goal=(
                "Establish temporal context by determining the current time, "
                "timezone, and DST status, then resolve human datetime "
                "expressions into precise RFC 3339 timestamps"
            ),
            tools=tools,
            allow_delegation=False,
            verbose=True,
        )

    def calendar_manager(self, tools):
        return Agent(
            role="Calendar Manager",
            backstory=(
                "You are a calendar operations specialist. You list calendars "
                "to discover connected providers (Google, Outlook, CalDAV), "
                "query events in time ranges, and find available slots using "
                "find_free_slots. You always use provider-prefixed calendar "
                "IDs (e.g., google/primary, outlook/work). You never assume "
                "calendar IDs — you discover them first with list_calendars."
            ),
            goal=(
                "Query connected calendars to find free time slots and "
                "check availability across all providers"
            ),
            tools=tools,
            allow_delegation=False,
            verbose=True,
        )

    def scheduling_coordinator(self, tools):
        return Agent(
            role="Scheduling Coordinator",
            backstory=(
                "You are the lead scheduler. You take resolved timestamps "
                "and available slots to select the best meeting time. You "
                "use book_slot to create the event — this tool uses "
                "Two-Phase Commit to acquire a lock, verify no conflicts "
                "exist, write the event, then release the lock. You never "
                "double-book."
            ),
            goal=(
                "Book a conflict-free meeting using the available slots "
                "and resolved timestamps from the other agents"
            ),
            tools=tools,
            allow_delegation=False,
            verbose=True,
        )
