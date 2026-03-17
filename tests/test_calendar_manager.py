import pytest
from unittest.mock import mock_open, patch
from icalendar import Calendar
from stuart_ai.agents.productivity.calendar_manager import CalendarManager
from stuart_ai.core.exceptions import ToolError


ICS_CONTENT = (
    "BEGIN:VCALENDAR\r\n"
    "PRODID:-//Stuart AI//EN\r\n"
    "VERSION:2.0\r\n"
    "BEGIN:VEVENT\r\n"
    "DTSTART:20231027T140000Z\r\n"
    "DTEND:20231027T150000Z\r\n"
    "SUMMARY:Existing Event\r\n"
    "UID:test-uid-1234\r\n"
    "END:VEVENT\r\n"
    "END:VCALENDAR\r\n"
)


@pytest.fixture
def calendar_manager(mocker):
    mocker.patch('os.path.exists', return_value=False)
    return CalendarManager(calendar_file="test_calendar.ics")


def test_load_calendar_no_file(calendar_manager):
    assert isinstance(calendar_manager.calendar, Calendar)
    assert len(calendar_manager._get_events()) == 0


def test_load_calendar_existing_file(mocker):
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('builtins.open', mock_open(read_data=ICS_CONTENT.encode()))

    manager = CalendarManager()
    events = manager._get_events()
    assert len(events) == 1
    assert str(events[0].get('SUMMARY')) == "Existing Event"


def test_load_calendar_error(mocker):
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('builtins.open', side_effect=IOError("Read Error"))

    manager = CalendarManager()
    assert len(manager._get_events()) == 0


def test_add_event_success(calendar_manager, mocker):
    mocker.patch('builtins.open', mock_open())

    result = calendar_manager.add_event("Meeting", "2023-10-27 14:00")

    assert "agendado para" in result
    events = calendar_manager._get_events()
    assert len(events) == 1
    assert str(events[0].get('SUMMARY')) == "Meeting"
    assert events[0].get('DTSTART').dt.year == 2023


def test_add_event_unparseable_date(calendar_manager):
    with pytest.raises(ToolError):
        calendar_manager.add_event("Meeting", "")


def test_list_events_empty(calendar_manager):
    result = calendar_manager.list_events()
    assert "Não há eventos agendados" in result


def test_list_events_success(calendar_manager, mocker):
    mocker.patch('builtins.open', mock_open())

    calendar_manager.add_event("Event 1", "2023-10-27 10:00")
    calendar_manager.add_event("Event 2", "2023-10-28 10:00")

    result = calendar_manager.list_events()

    assert "Event 1" in result
    assert "Event 2" in result


def test_list_events_filtered(calendar_manager, mocker):
    mocker.patch('builtins.open', mock_open())

    calendar_manager.add_event("Event Today", "2023-10-27 10:00")
    calendar_manager.add_event("Event Tomorrow", "2023-10-28 10:00")

    result = calendar_manager.list_events("2023-10-27")
    assert "Event Today" in result
    assert "Event Tomorrow" not in result


def test_delete_event_success(calendar_manager, mocker):
    mocker.patch('builtins.open', mock_open())

    calendar_manager.add_event("To Delete", "2023-10-27 10:00")
    assert len(calendar_manager._get_events()) == 1

    result = calendar_manager.delete_event("To Delete")

    assert "removido(s) com sucesso" in result
    assert len(calendar_manager._get_events()) == 0


def test_delete_event_not_found(calendar_manager):
    result = calendar_manager.delete_event("Non Existent")
    assert "Nenhum evento encontrado" in result
