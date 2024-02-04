import os
import datetime
from datetime import datetime, timedelta
import locale
import caldav
from caldav.elements import dav, cdav
from event import Event


url=os.environ.get("CAL_URL")
user=os.environ.get("CAL_USER")
password=os.environ.get("CAL_PASS")


def connect(url, user, password, calendar):
    client = caldav.DAVClient(url=url, username=user, password=password)
    return client.principal().calendar(name=calendar)

def get_events(calendar: str) -> list:
    event_list = []
    cal = connect(url, user, password, calendar)        

    # Fetch todays events
    events = cal.date_search(datetime.date.today(), datetime.date.today() + datetime.timedelta(days=1))

    # Get the events and push them to stdout
    for event in events:
        event.load()
        e = event.instance.vevent
        event_list.append(Event(e.dtstart.value.strftime('%H:%M'), e.summary.value))
    return(event_list)

def add_event(calendar, summary, start, duration):
    event_start = parse_date_from_voice(start) 
    event_end = event_start + timedelta(hours=duration)

    cal = connect(url, user, password, calendar)
    cal.save_event(dtstart=event_start,
                   dtend=event_end,
                   summary=summary)

def parse_date_from_voice(date_text):
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    PATTERN = "%d de %B de %Y a las %H:%M"
    return datetime.strptime(date_text,PATTERN)

def print_events(calendar):
    for event in calendar.events():
        ical_text = event.data
        print(ical_text)

if __name__ == "__main__":
    today_events=get_events("Personal")
    print(today_events)