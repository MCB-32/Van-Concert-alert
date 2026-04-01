import requests
from bs4 import BeautifulSoup
import json
import hashlib
from playwright.sync_api import sync_playwright

URL = "https://admitone.com/events/vancouver/pro/concerts"  # confirm this is still correct

def get_events():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL)

        page.wait_for_timeout(5000)

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    events = []

    for item in soup.select("a"):
        text = item.get_text(strip=True)

        if len(text) > 20:
            event_id = hashlib.md5(text.encode()).hexdigest()

            events.append({
                "id": event_id,
                "title": text
            })

    return events
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
