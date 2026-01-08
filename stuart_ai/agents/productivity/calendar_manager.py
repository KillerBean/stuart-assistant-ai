from __future__ import annotations
import os
from datetime import datetime, timedelta
from ics import Calendar, Event
from dateutil import parser
from stuart_ai.core.logger import logger
from stuart_ai.core.exceptions import ToolError

class CalendarManager:
    def __init__(self, calendar_file="stuart_calendar.ics"):
        self.calendar_file = os.path.join(os.getcwd(), calendar_file)
        self.calendar = self._load_calendar()

    def _load_calendar(self) -> Calendar:
        """Loads the calendar from the file or creates a new one."""
        if os.path.exists(self.calendar_file):
            try:
                with open(self.calendar_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Handle empty file case
                    if not content.strip():
                        return Calendar()
                    return Calendar(content)
            except (IOError, ValueError) as e:
                logger.error("Failed to load calendar: %s", e)
                return Calendar()
        return Calendar()

    def _save_calendar(self):
        """Saves the current calendar state to the file."""
        try:
            with open(self.calendar_file, 'w', encoding='utf-8') as f:
                f.writelines(self.calendar) # type: ignore
        except IOError as e:
            logger.error("Failed to save calendar: %s", e)
            raise ToolError("Não foi possível salvar o evento no calendário.")

    def add_event(self, title: str, start_str: str, duration_minutes: int = 60) -> str:
        """Adds an event to the calendar."""
        try:
            # Parse natural language date string using dateutil (fuzzy=True allows partial parsing)
            # Note: For production, a stronger NL date parser like dateparser is better, 
            # but dateutil works for explicit dates.
            start_dt = parser.parse(start_str, fuzzy=True, dayfirst=True)
            
            # If the parsed date is in the past (and no year specified), dateutil might default to current year.
            # We assume user means future. Logic could be improved here.
            
            end_dt = start_dt + timedelta(minutes=duration_minutes)
            
            event = Event()
            event.name = title
            event.begin = start_dt
            event.end = end_dt
            
            self.calendar.events.add(event)
            self._save_calendar()
            
            return f"Evento '{title}' agendado para {start_dt.strftime('%d/%m/%Y às %H:%M')}."
        except (ValueError, TypeError) as e:
            logger.error("Error adding event: %s", e)
            raise ToolError(f"Erro ao agendar evento: {e}")

    def list_events(self, date_str: str | None = None) -> str:
        """Lists events, optionally filtering by a specific date."""
        if not self.calendar.events:
            return "Não há eventos agendados."

        try:
            if date_str:
                target_date = parser.parse(date_str, fuzzy=True, dayfirst=True).date()
                events = [e for e in self.calendar.events if e.begin.date() == target_date]
                period_msg = f"para {target_date.strftime('%d/%m/%Y')}"
            else:
                # List future events by default if no date
                now = datetime.now(self.calendar.events[0].begin.tzinfo) # type: ignore # Match timezone if possible
                # Simple comparison logic depends on tz awareness. ics uses arrow which is tz aware.
                # Let's just list all sorted.
                events = sorted(self.calendar.events, key=lambda x: x.begin)
                period_msg = "na sua agenda"

            if not events:
                return f"Nenhum evento encontrado {period_msg}."

            result = [f"Agenda {period_msg}:"]
            for event in events:
                # Format: 14:00 - Reunião
                # Convert arrow to datetime for strftime
                start_fmt = event.begin.format('DD/MM/YYYY HH:mm')
                result.append(f"- {start_fmt}: {event.name}")
            
            return "\n".join(result)

        except (ValueError, TypeError) as e:
            logger.error("Error listing events: %s", e)
            return "Erro ao ler a agenda."

    def delete_event(self, title: str, date_str: str | None = None) -> str:
        """Deletes an event by title, optionally filtering by date."""
        try:
            to_delete = []
            for event in self.calendar.events:
                if event.name.lower() == title.lower():
                    if date_str:
                        target_date = parser.parse(date_str, fuzzy=True, dayfirst=True).date()
                        if event.begin.date() == target_date:
                            to_delete.append(event)
                    else:
                        to_delete.append(event)

            if not to_delete:
                return f"Nenhum evento encontrado com o título '{title}'."

            for event in to_delete:
                self.calendar.events.remove(event)

            self._save_calendar()
            return f"Evento(s) '{title}' removido(s) com sucesso."

        except (ValueError, TypeError) as e:
            logger.error("Error deleting event: %s", e)
            raise ToolError(f"Erro ao remover evento: {e}")