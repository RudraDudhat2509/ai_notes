"""
EXERCISE 01 — RATE LIMITER
==========================
System design interviews love this. You need to implement a rate limiter
from scratch using only a Python dict (no Redis, no libraries).

GOAL: allow max N requests per user per time window (in seconds).
If the user exceeds N requests in the window, return False.

YOUR TASK: implement the two functions below.
Run this file. All tests must pass.

Do NOT use any imports except time (already imported).
"""

import time


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        """
        max_requests  — how many requests allowed per window
        window_seconds — the time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.store = {}   # you can use this dict however you want

    def is_allowed(self, user_id: str) -> bool:
        """
        Returns True if the request is allowed.
        Returns False if the user has exceeded max_requests in the current window.

        YOU IMPLEMENT THIS.
        """
        self.now=time.time()
        if user_id not in self.store:
            self.store[user_id]={"count":0 , "window":self.now}
        if time.time()-self.store[user_id]["window"]>self.window_seconds:
            self.store[user_id]={"count":0 , "window":self.now}
        self.store[user_id]["count"]+=1
        if self.store[user_id]["count"]>self.max_requests:
            return False
        return True
        


# ── TESTS ── do not modify below this line ──────────────────────────────────

def test_basic_allow():
    rl = RateLimiter(max_requests=3, window_seconds=10)
    assert rl.is_allowed("user1") == True
    assert rl.is_allowed("user1") == True
    assert rl.is_allowed("user1") == True
    print("✓ test_basic_allow passed")

def test_basic_block():
    rl = RateLimiter(max_requests=3, window_seconds=10)
    rl.is_allowed("user1")
    rl.is_allowed("user1")
    rl.is_allowed("user1")
    assert rl.is_allowed("user1") == False   # 4th request — blocked
    print("✓ test_basic_block passed")

def test_different_users():
    rl = RateLimiter(max_requests=2, window_seconds=10)
    rl.is_allowed("user1")
    rl.is_allowed("user1")
    assert rl.is_allowed("user1") == False   # user1 blocked
    assert rl.is_allowed("user2") == True    # user2 unaffected
    print("✓ test_different_users passed")

def test_window_reset():
    rl = RateLimiter(max_requests=2, window_seconds=1)
    rl.is_allowed("user1")
    rl.is_allowed("user1")
    assert rl.is_allowed("user1") == False   # blocked
    time.sleep(1.1)                           # wait for window to expire
    assert rl.is_allowed("user1") == True    # window reset, allowed again
    print("✓ test_window_reset passed")

if __name__ == "__main__":
    test_basic_allow()
    test_basic_block()
    test_different_users()
    test_window_reset()
    print("\nAll tests passed.")
