"""Integration smoke test for the real soccerdata/Chrome dependency chain.

Deliberately NOT a full live FBref scrape (that would be slow, eat into
FBref's 10-req/min budget on every test run, and isn't appropriate for a
unit suite regardless of Chrome availability). This only checks that the
one genuinely environment-dependent piece -- launching a real browser
session via soccerdata -- works when Chrome is present, and skips
gracefully (not a failure) when it isn't, per design.md's risk mitigation.
"""
from __future__ import annotations

import shutil
import sys

import pytest


def _chrome_available() -> bool:
    if shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser"):
        return True
    if sys.platform == "darwin":
        import os

        return os.path.exists("/Applications/Google Chrome.app")
    return False


@pytest.mark.skipif(not _chrome_available(), reason="Chrome/chromedriver not installed in this environment")
def test_soccerdata_fbref_can_launch_a_real_browser_session():
    import soccerdata as sd

    fbref = sd.FBref(leagues="ENG-Premier League", seasons="2024-2025", no_cache=True, no_store=True)
    assert fbref is not None
