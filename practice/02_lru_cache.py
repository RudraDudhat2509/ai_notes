"""
EXERCISE 02 — LRU CACHE
========================
Classic system design + coding interview question.
Asked at Google, Meta, Portkey, everywhere.

LRU = Least Recently Used.
When the cache is full and a new item comes in, evict the item
that was used LEAST recently (i.e. the oldest untouched item).

EXAMPLE:
  cache = LRUCache(capacity=3)
  cache.put("a", 1)   # cache: a
  cache.put("b", 2)   # cache: a, b
  cache.put("c", 3)   # cache: a, b, c
  cache.get("a")      # cache: b, c, a  (a is now most recently used)
  cache.put("d", 4)   # cache is full — evict b (least recently used)
                      # cache: c, a, d

YOUR TASK: implement get() and put().

RULES:
- get(key) returns the value if key exists, else returns -1
- put(key, value) inserts or updates. If at capacity, evict LRU item first.
- Both get() and put() must be O(1) time complexity.

HINT: Python's dict remembers insertion order (Python 3.7+).
      You can use this to track order without extra data structures.
      Look up: dict.move_to_end(), dict.popitem()
"""

from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: str) -> int:
        """
        Return value if key exists, else -1.
        Accessing a key makes it the most recently used.

        YOU IMPLEMENT THIS.
        """
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)  # mark as most recently used
        return self.cache[key]
        

    def put(self, key: str, value: int) -> None:
        """
        Insert or update key-value pair.
        If key exists, update value and mark as most recently used.
        If at capacity, evict least recently used item first.

        YOU IMPLEMENT THIS.
        """
        if key in self.cache: 
            self.cache.move_to_end(key)
            self.cache[key]=value
        else: 
            self.cache[key]=value   
            if self.capacity<len(self.cache):
                self.cache.popitem(last=False)
       
        return 


# ── TESTS ── do not modify below this line ──────────────────────────────────

def test_basic_get_put():
    c = LRUCache(3)
    c.put("a", 1)
    c.put("b", 2)
    assert c.get("a") == 1
    assert c.get("z") == -1   # missing key
    print("✓ test_basic_get_put passed")

def test_eviction():
    c = LRUCache(3)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)
    c.put("d", 4)           # should evict "a" (least recently used)
    assert c.get("a") == -1  # evicted
    assert c.get("b") == 2
    assert c.get("d") == 4
    print("✓ test_eviction passed")

def test_get_updates_order():
    c = LRUCache(3)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)
    c.get("a")              # a is now most recently used
    c.put("d", 4)           # should evict "b" (now the least recently used)
    assert c.get("b") == -1  # evicted
    assert c.get("a") == 1   # still there
    print("✓ test_get_updates_order passed")

def test_update_existing():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("a", 99)          # update existing — should not evict anything
    assert c.get("a") == 99
    assert c.get("b") == 2
    print("✓ test_update_existing passed")

if __name__ == "__main__":
    test_basic_get_put()
    test_eviction()
    test_get_updates_order()
    test_update_existing()
    print("\nAll tests passed.")
