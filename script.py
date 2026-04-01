import requests
from bs4 import BeautifulSoup
import json
import hashlib

URL = "https://admitone.com/events/vancouver/pro/concerts"  # confirm this is still correct

def get_events():
    res = requests.get(URL)
    soup = BeautifulSoup(res.text, "html.parser")

    events = []

    for item in soup.select(".event"):  # selector may need adjusting
        artist = item.select_one(".event-title").text.strip()
        date = item.select_one(".event-date").text.strip()
        venue = item.select_one(".event-venue").text.strip()

        event_id = hashlib.md5(f"{artist}{date}{venue}".encode()).hexdigest()

        events.append({
            "id": event_id,
            "artist": artist,
            "date": date,
            "venue": venue
        })

    return events


def load_existing():
    try:
        with open("events.json", "r") as f:
            return json.load(f)
    except:
        return []


def save(events):
    with open("events.json", "w") as f:
        json.dump(events, f, indent=2)


def main():
    new_events = get_events()
    existing = load_existing()

    existing_ids = {e["id"] for e in existing}

    truly_new = [e for e in new_events if e["id"] not in existing_ids]

    if truly_new:
        print("NEW EVENTS FOUND:")
        for e in truly_new:
            print(f"{e['artist']} - {e['date']} @ {e['venue']}")
    else:
        print("No new events.")

    save(new_events)


if __name__ == "__main__":
    main()
