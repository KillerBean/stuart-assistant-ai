import pytest
from unittest.mock import mock_open, MagicMock, patch
from stuart_ai.agents.productivity.calendar_manager import CalendarManager
from stuart_ai.core.exceptions import ToolError
from ics import Calendar, Event
from datetime import datetime, timedelta

@pytest.fixture
def calendar_manager(mocker):
    # Mock os.path.exists to return False initially (no file)
    mocker.patch('os.path.exists', return_value=False)
    return CalendarManager(calendar_file="test_calendar.ics")

def test_load_calendar_no_file(calendar_manager):
    assert isinstance(calendar_manager.calendar, Calendar)
    assert len(calendar_manager.calendar.events) == 0

def test_load_calendar_existing_file(mocker):
    ics_content = "BEGIN:VCALENDAR\nPRODID:ics.py - http://git.io/lLljaA\nVERSION:2.0\nBEGIN:VEVENT\nDTSTART:20231027T140000Z\nSUMMARY:Existing Event\nEND:VEVENT\nEND:VCALENDAR"
    
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('builtins.open', mock_open(read_data=ics_content))
    
    manager = CalendarManager()
    assert len(manager.calendar.events) == 1
    assert list(manager.calendar.events)[0].name == "Existing Event"

def test_load_calendar_error(mocker):
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('builtins.open', side_effect=IOError("Read Error"))
    
    # Should safely return empty calendar and log error (we can spy log if we want)
    manager = CalendarManager()
    assert len(manager.calendar.events) == 0

def test_add_event_success(calendar_manager, mocker):
    mock_file = mock_open()
    mocker.patch('builtins.open', mock_file)
    
    result = calendar_manager.add_event("Meeting", "2023-10-27 14:00")
    
    assert "agendado para" in result
    assert len(calendar_manager.calendar.events) == 1
    event = list(calendar_manager.calendar.events)[0]
    assert event.name == "Meeting"
    # ics stores in UTC or as provided. dateutil parse returns naive if no TZ.
    # We should check if it parsed correctly.
    assert event.begin.year == 2023
    
    mock_file().writelines.assert_called()

def test_add_event_error(calendar_manager, mocker):
    mocker.patch('dateutil.parser.parse', side_effect=ValueError("Invalid Date"))
    
    with pytest.raises(ToolError):
        calendar_manager.add_event("Meeting", "Invalid Date")

def test_list_events_empty(calendar_manager):
    result = calendar_manager.list_events()
    assert "Não há eventos agendados" in result

def test_list_events_success(calendar_manager, mocker):
    mocker.patch('builtins.open', mock_open())
    
    # Add two events
    calendar_manager.add_event("Event 1", "2023-10-27 10:00")
    calendar_manager.add_event("Event 2", "2023-10-28 10:00")
    
    result = calendar_manager.list_events()
    
    assert "Event 1" in result
    assert "Event 2" in result

def test_list_events_filtered(calendar_manager, mocker):
    mocker.patch('builtins.open', mock_open())
    
    calendar_manager.add_event("Event Today", "2023-10-27 10:00")
    calendar_manager.add_event("Event Tomorrow", "2023-10-28 10:00")
    
    # Check filter
    result = calendar_manager.list_events("2023-10-27")
    assert "Event Today" in result
    assert "Event Tomorrow" not in result

def test_delete_event_success(calendar_manager, mocker):
    mocker.patch('builtins.open', mock_open())
    
    calendar_manager.add_event("To Delete", "2023-10-27 10:00")
    assert len(calendar_manager.calendar.events) == 1
    
    result = calendar_manager.delete_event("To Delete")
    
    assert "removido(s) com sucesso" in result
    assert len(calendar_manager.calendar.events) == 0

def test_delete_event_not_found(calendar_manager):
    result = calendar_manager.delete_event("Non Existent")
    assert "Nenhum evento encontrado" in result
