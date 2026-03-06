from crewai import Task


class CalendarTasks:
    def orient_in_time(self, agent, meeting_time):
        return Task(
            description=(
                f"Get the current temporal context: call get_temporal_context "
                f"to learn the current time, timezone, UTC offset, and DST "
                f"status. Then resolve the meeting time expression "
                f"'{meeting_time}' into a precise RFC 3339 timestamp "
                f"using resolve_datetime."
            ),
            expected_output=(
                "The current local time, timezone, DST status, and the "
                "resolved RFC 3339 timestamp for the requested meeting time."
            ),
            agent=agent,
        )

    def find_availability(self, agent):
        return Task(
            description=(
                "Using the resolved timestamp from the previous task, "
                "find available time slots on the target date. First call "
                "list_calendars to discover connected providers and their "
                "calendar IDs. Then call find_free_slots for the primary "
                "calendar on the target date to find 30-minute available "
                "windows. Report all available slots."
            ),
            expected_output=(
                "A list of connected calendars and available 30-minute time "
                "slots on the target date, with start/end times in RFC 3339 "
                "format and the calendar ID to use for booking."
            ),
            agent=agent,
        )

    def book_meeting(self, agent, meeting_title):
        return Task(
            description=(
                f"From the available slots found in the previous task, "
                f"select the best slot and book a 30-minute meeting "
                f"titled '{meeting_title}'. Use the book_slot tool with "
                f"the calendar ID from the Calendar Manager. The book_slot "
                f"tool uses Two-Phase Commit to prevent double-bookings."
            ),
            expected_output=(
                "Confirmation that the meeting was booked, including the "
                "calendar ID, event title, start time, and end time."
            ),
            agent=agent,
        )
