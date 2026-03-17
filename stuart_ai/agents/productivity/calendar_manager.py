from __future__ import annotations
import os
import uuid
from datetime import timedelta
from icalendar import Calendar, Event
import dateparser
from stuart_ai.core.logger import logger
from stuart_ai.core.exceptions import ToolError


class CalendarManager:
    def __init__(self, calendar_file="stuart_calendar.ics"):
        self.calendar_file = os.path.join(os.getcwd(), calendar_file)
        self.calendar = self._load_calendar()

    def _load_calendar(self) -> Calendar:
        if os.path.exists(self.calendar_file):
            try:
                with open(self.calendar_file, 'rb') as f:
                    return Calendar.from_ical(f.read())
            except (IOError, ValueError) as e:
                logger.error("Failed to load calendar: %s", e)
                return self._new_calendar()
        return self._new_calendar()

    @staticmethod
    def _new_calendar() -> Calendar:
        cal = Calendar()
        cal.add('prodid', '-//Stuart AI//EN')
        cal.add('version', '2.0')
        return cal

    def _save_calendar(self):
        try:
            with open(self.calendar_file, 'wb') as f:
                f.write(self.calendar.to_ical())
        except IOError as e:
            logger.error("Failed to save calendar: %s", e)
            raise ToolError("Não foi possível salvar o evento no calendário.") from e

    def _get_events(self) -> list:
        return [c for c in self.calendar.walk() if c.name == 'VEVENT']

    def add_event(self, title: str, start_str: str, duration_minutes: int = 60) -> str:
        try:
            start_dt = dateparser.parse(start_str)
            if not start_dt:
                raise ToolError(f"Não consegui entender a data: '{start_str}'")

            end_dt = start_dt + timedelta(minutes=duration_minutes)

            event = Event()
            event.add('summary', title)
            event.add('dtstart', start_dt)
            event.add('dtend', end_dt)
            event.add('uid', str(uuid.uuid4()))

            self.calendar.add_component(event)
            self._save_calendar()

            return f"Evento '{title}' agendado para {start_dt.strftime('%d/%m/%Y às %H:%M')}."
        except (ValueError, TypeError) as e:
            logger.error("Error adding event: %s", e)
            raise ToolError(f"Erro ao agendar evento: {e}") from e

    def list_events(self, date_str: str | None = None) -> str:
        events = self._get_events()
        if not events:
            return "Não há eventos agendados."

        try:
            if date_str:
                target_dt = dateparser.parse(date_str)
                if not target_dt:
                    return f"Não entendi a data '{date_str}'."

                target_date = target_dt.date()
                events_to_show = [
                    e for e in events
                    if self._event_date(e) == target_date
                ]
                period_msg = f"para {target_date.strftime('%d/%m/%Y')}"
            else:
                events_to_show = sorted(events, key=lambda e: e.get('DTSTART').dt)
                period_msg = "na sua agenda"

            if not events_to_show:
                return f"Nenhum evento encontrado {period_msg}."

            result = [f"Agenda {period_msg}:"]
            for event in events_to_show:
                dt = event.get('DTSTART').dt
                name = str(event.get('SUMMARY', 'Sem título'))
                start_fmt = dt.strftime('%d/%m/%Y %H:%M') if hasattr(dt, 'strftime') else str(dt)
                result.append(f"- {start_fmt}: {name}")

            return "\n".join(result)

        except (ValueError, TypeError) as e:
            logger.error("Error listing events: %s", e)
            return "Erro ao ler a agenda."

    def delete_event(self, title: str, date_str: str | None = None) -> str:
        try:
            to_delete = [
                c for c in self.calendar.walk()
                if c.name == 'VEVENT'
                and str(c.get('SUMMARY', '')).lower() == title.lower()
                and (
                    not date_str
                    or self._matches_date(c, date_str)
                )
            ]

            if not to_delete:
                return f"Nenhum evento encontrado com o título '{title}'."

            for component in to_delete:
                self.calendar.subcomponents.remove(component)

            self._save_calendar()
            return f"Evento(s) '{title}' removido(s) com sucesso."

        except (ValueError, TypeError) as e:
            logger.error("Error deleting event: %s", e)
            raise ToolError(f"Erro ao remover evento: {e}") from e

    @staticmethod
    def _event_date(event):
        dt = event.get('DTSTART').dt
        return dt.date() if hasattr(dt, 'date') else dt

    @staticmethod
    def _matches_date(event, date_str: str) -> bool:
        target_dt = dateparser.parse(date_str)
        if not target_dt:
            return False
        dt = event.get('DTSTART').dt
        event_date = dt.date() if hasattr(dt, 'date') else dt
        return event_date == target_dt.date()
