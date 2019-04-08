import requests
import time
from threading import Timer

from ..config import API_CFG
from ..helpers.utils import get_players

# tokens
_access_token = None
_refresh_token = None

# expiry times in seconds since epoch
_access_token_expires = None
_refresh_token_expires = None

# threading.Timer for refreshing tokens
_refresh_timer = None

# how many seconds before expiry time to refresh tokens
_refresh_time_gap = 60


def on_load():
    """Call this on plugin load to authenticate with the api."""

    if API_CFG["authenticate"]:
        authenticate()
    
    for player in get_players():
        Player.add_player(player.playerinfo, player.index)


def on_unload():
    """Call this on plugin unload to revoke JWT tokens
    and to stop refresh timer thread."""

    if not API_CFG["authenticate"]:
        return

    if _access_token and time.time() < _access_token_expires:
        revoke_token(_access_token, "access")

    if _refresh_token and time.time() < _refresh_token_expires:
        revoke_token(_refresh_token, "refresh")

    if _refresh_timer:
        _refresh_timer.cancel()


def authenticate():
    """Authenticate with the api."""

    # make sure we're using https
    assert API_CFG["host"].startswith("https://")

    r = requests.post(
        API_CFG["host"] + "/token/auth",
        headers={"Content-Type": "application/json"},
        json={"username": API_CFG["username"], "password": API_CFG["password"]},
    )

    if r.status_code != 200:
        print("[jtimer] Failed to authenticate with the api.")
        print(r.content)
        return

    data = r.json()

    # validate data
    if data is None:
        print(f"[jtimer] Failed to parse response from '/token/auth'.")
        print(r.content)

    if "access_token" not in data.keys():
        print("[jtimer] Authentication response is missing access_token.")
        print(r.content)

    if "refresh_token" not in data.keys():
        print("[jtimer] Authentication response is missing refresh_token.")
        print(r.content)

    if "access_token_expires_in" not in data.keys():
        print("[jtimer] Authentication response is missing access_token_expires_in.")
        print(r.content)

    if "refresh_token_expires_in" not in data.keys():
        print("[jtimer] Authentication response is missing refresh_token_expires_in.")
        print(r.content)

    global _access_token, _refresh_token, _access_token_expires, _refresh_token_expires
    old_refresh = None
    if _refresh_token:
        old_refresh = _refresh_token

    old_access = None
    if _access_token:
        old_access = _access_token

    _access_token = data["access_token"]
    _refresh_token = data["refresh_token"]
    _access_token_expires = time.time() + data["access_token_expires_in"]
    _refresh_token_expires = time.time() + data["refresh_token_expires_in"]

    if old_refresh:
        revoke_token(old_refresh, "refresh")

    if old_access:
        revoke_token(old_access, "access")

    print("[jtimer] Authenticated with the api!")

    future_auth()


def refresh_access():
    """Use refresh token to get new access token."""

    # make sure we're using https
    assert API_CFG["host"].startswith("https://")

    r = requests.post(
        API_CFG["host"] + "/token/refresh",
        headers={"Authorization": f"Bearer {_refresh_token}"},
    )

    if r.status_code != 200:
        print("[jtimer] Failed to refresh access_token.")
        print(r.content)
        return

    data = r.json()

    if data is None:
        print(f"[jtimer] Failed to parse response from '/token/refresh'.")
        print(r.content)

    # validate data
    if "access_token" not in data.keys():
        print("[jtimer] Refresh response is missing access_token.")
        print(r.content)

    if "expires_in" not in data.keys():
        print("[jtimer] Refresh response is missing expires_in.")
        print(r.content)

    global _access_token, _access_token_expires
    old_access = _access_token
    _access_token = data["access_token"]
    _access_token_expires = time.time() + data["expires_in"]

    print("[jtimer] Refreshed access token.")

    revoke_token(old_access, "access")
    future_auth()


def future_auth():
    """Start timer for refreshing access token, or authenticating again for a new refresh token."""
    if _access_token_expires and _refresh_token_expires:
        global _refresh_timer
        if _access_token_expires < _refresh_token_expires:
            if _refresh_timer:
                _refresh_timer.cancel()

            delay = _access_token_expires - time.time() - _refresh_time_gap
            if delay > 0:
                _refresh_timer = Timer(delay, refresh_access)
                _refresh_timer.start()
            else:
                refresh_access()

        else:
            if _refresh_timer:
                _refresh_timer.cancel()

            delay = _refresh_token_expires - time.time() - _refresh_time_gap
            if delay > 0:
                _refresh_timer = Timer(delay, authenticate)
                _refresh_timer.start()
            else:
                authenticate()

    else:
        print("[jtimer] Tried to queue future authentication without expiry times.")


def revoke_token(token, token_type):
    """Revoke a token."""
    assert token_type in ["access", "refresh"]

    # make sure we're using https
    assert API_CFG["host"].startswith("https://")

    r = requests.post(
        API_CFG["host"] + f"/token/revoke/{token_type}",
        headers={"Authorization": f"Bearer {token}"},
    )

    if r.status_code != 200:
        print(f"[jtimer] Failed to revoke {token_type} token.")
        print(r.content)
        return

    print(f"[jtimer] Revoked {token_type} token.")


def get_token():
    return _access_token
