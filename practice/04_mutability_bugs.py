"""
EXERCISE 04 — MUTABILITY & REFERENCE BUG HUNT
==============================================
Phase 1, Week 1 — Python object & memory model.

Everything below is REAL production-shaped code (agent state, per-user memory,
config building). Each function has a reference/mutability bug that flows from
the object model. Your job: FIX each one so the tests pass.

DO NOT change the tests. Only fix the functions above the test line.

RULES:
  - No copy-paste from notes. Reason from the object model.
  - For each fix, you should be able to say WHY the original was wrong.

Run:  python 04_mutability_bugs.py
"""

from dataclasses import dataclass, field


# ── BUG 1 ───────────────────────────────────────────────────────────────────
# A helper that should ADD a message WITHOUT mutating the caller's history.
# (Think: building a prompt variant while keeping the original conversation.)
def with_system_note(history: list, note: str) -> list:
    
    return history + [{"role": "system", "content": note}]


# ── BUG 2 ───────────────────────────────────────────────────────────────────
# Per-user memory loader. Every NEW user with no saved memory should start
# with a FRESH empty memory list. Right now they share one.
def get_user_memory(user_id: str, memory=None) -> list:
    if memory is None:
        memory=[]
    memory.append(f"session_started:{user_id}")
    return memory


# ── BUG 3 ───────────────────────────────────────────────────────────────────
# Agent config dataclass. Every Agent instance should get its OWN tools list.
# Right now... see for yourself.
@dataclass
class Agent:
    name: str
    tools: list = field(default_factory=list)         # <-- something is wrong here

    def add_tool(self, tool: str):
        self.tools.append(tool)


# ── BUG 4 ───────────────────────────────────────────────────────────────────
# Dedup function — should return unique items, order doesn't matter.
# It tries to use a set but crashes on some inputs. Make it robust.
def dedup(items: list) -> set:
    # a set is a hash table -> every element must be hashable (immutable).
    # lists are mutable -> unhashable -> convert each to its immutable twin, a
    # tuple, before adding. (1,2) and (1,2) hash equal, so they dedupe correctly.
    return {tuple(x) if isinstance(x, list) else x for x in items}

# ── TESTS ── do not modify below this line ──────────────────────────────────

def test_bug1_no_mutation():
    convo = [{"role": "user", "content": "hi"}]
    variant = with_system_note(convo, "be concise")
    assert len(variant) == 2
    assert len(convo) == 1, "caller's history was mutated!"
    print("✓ bug1 fixed")

def test_bug2_fresh_memory():
    a = get_user_memory("alice")
    b = get_user_memory("bob")
    assert a == ["session_started:alice"], f"alice got {a}"
    assert b == ["session_started:bob"], f"bob got {b}"
    print("✓ bug2 fixed")

def test_bug3_separate_tools():
    a1 = Agent("researcher")
    a2 = Agent("writer")
    a1.add_tool("search")
    assert a1.tools == ["search"]
    assert a2.tools == [], f"writer shares researcher's tools: {a2.tools}"
    print("✓ bug3 fixed")

def test_bug4_dedup_robust():
    assert dedup([1, 1, 2, 3, 3]) == {1, 2, 3}
    # must not crash on unhashable elements — dedup the lists too
    out = dedup([[1, 2], [1, 2], [3]])
    assert len(out) == 2
    print("✓ bug4 fixed")

if __name__ == "__main__":
    test_bug1_no_mutation()
    test_bug2_fresh_memory()
    test_bug3_separate_tools()
    test_bug4_dedup_robust()
    print("\nAll bugs fixed.")
