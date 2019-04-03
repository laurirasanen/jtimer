import json
import requests

from ..config import API_CFG
from .auth import get_token


def map_times(map_id, start=1, limit=50):
    """Get map times from the api"""
    assert map_id > 0
    assert start > 0
    assert limit <= 50

    times = None
    r = requests.get(
        API_CFG["host"] + f"/times/map/{map_id}",
        params={"start": start, "limit": limit},
    )
    if r.status_code == 200:
        times = r.json()
    return times


def add_map_time(map_id, player_id, player_class, start_time, end_time):
    """Add time to map"""
    if not API_CFG["authenticate"]:
        return

    assert map_id > 0
    assert player_id > 0
    assert player_class in [2, 4]
    assert start_time > 0
    assert end_time > 0 and end_time > start_time

    access_token = get_token()
    if access_token is None:
        return None

    r = requests.post(
        API_CFG["host"] + f"/times/insert/map/{map_id}",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        data=json.dumps(
            {
                "player_id": player_id,
                "player_class": player_class,
                "start_time": start_time,
                "end_time": end_time,
            }
        ),
    )

    result = None
    if r.status_code == 200:
        result = r.json()
    else:
        print(f"[jtimer] failed to upload map time.")
        print(f"api response: {r.status_code}")
        print(r.content)

    return result
