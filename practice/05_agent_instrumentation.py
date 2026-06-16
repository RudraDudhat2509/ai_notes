"""
EXERCISE 05 — AGENT INSTRUMENTATION
=====================================
Phase 1, Week 2 — closures, decorators, generators, context managers.

Real scenario: you're evaluating an agent's tool-calling behavior.
You need to:
  1. Track how many times each tool was called (decorator + closure)
  2. Stream attack inputs lazily into the agent (generator)
  3. Guarantee a "run context" is always cleaned up (context manager)

All four Week 2 concepts in one real-shaped tool.
This is the skeleton of what you'd build for agent red-teaming.

YOUR TASK: implement the four marked functions.
DO NOT modify the tests.

Run:  python 05_agent_instrumentation.py
"""

from contextlib import contextmanager


# ── PART 1: DECORATOR ──────────────────────────────────────────────────────
# Build a decorator that counts how many times a function is called.
# The COUNT must persist across calls (use a closure).
# The decorated function must still return the original return value.
# Attach the count as a .call_count attribute on the wrapper so tests can read it.

def counted(func):
    """
    Decorator. Wraps func. Tracks how many times it has been called.
    Exposes the count via wrapper.call_count.

    YOU IMPLEMENT THIS.
    """
    pass


# ── PART 2: GENERATOR ──────────────────────────────────────────────────────
# Build a generator that yields attack prompts one at a time.
# It should yield each prompt from the list, but SKIP any that contain
# the word "safe" (case-insensitive). Lazy — nothing computed upfront.

def attack_prompt_stream(prompts: list):
    """
    Generator. Yields each prompt from `prompts`, skipping ones that
    contain the word 'safe' (case-insensitive).

    YOU IMPLEMENT THIS.
    """
    pass


# ── PART 3: CONTEXT MANAGER ────────────────────────────────────────────────
# Build a context manager using @contextmanager.
# On enter: print "=== run started ===" and yield a dict {"tool_calls": 0}
#           (callers use this dict to track state during the run)
# On exit:  ALWAYS print "=== run finished ===" — even if an exception occurred.
#           Do NOT suppress exceptions.

@contextmanager
def agent_run():
    """
    Context manager for one agent evaluation run.
    Yields a state dict {"tool_calls": 0} for callers to update.
    Guarantees cleanup print on exit, even on exception.

    YOU IMPLEMENT THIS.
    """
    pass


# ── TESTS ── do not modify below this line ──────────────────────────────────

def fake_tool(client_id: str) -> str:
    return f"data for {client_id}"

def test_counted_decorator():
    tool = counted(fake_tool)
    assert tool.call_count == 0
    tool("client-001")
    tool("client-002")
    tool("client-003")
    assert tool.call_count == 3
    assert tool("client-004") == "data for client-004"   # still returns original value
    assert tool.call_count == 4
    print("✓ test_counted_decorator passed")

def test_counted_independent():
    # each decorated function gets its OWN counter (own backpack)
    tool_a = counted(fake_tool)
    tool_b = counted(fake_tool)
    tool_a("x"); tool_a("y")
    tool_b("z")
    assert tool_a.call_count == 2
    assert tool_b.call_count == 1
    print("✓ test_counted_independent passed")

def test_attack_stream_filters():
    prompts = [
        "ignore previous instructions",
        "this is a safe prompt",
        "exfiltrate system prompt",
        "Safe mode activated",
        "jailbreak attempt",
    ]
    result = list(attack_prompt_stream(prompts))
    assert "this is a safe prompt" not in result
    assert "Safe mode activated" not in result
    assert "ignore previous instructions" in result
    assert "exfiltrate system prompt" in result
    assert "jailbreak attempt" in result
    assert len(result) == 3
    print("✓ test_attack_stream_filters passed")

def test_attack_stream_lazy():
    # generator should be lazy — calling it returns a generator object, not a list
    import types
    gen = attack_prompt_stream(["prompt one", "prompt two"])
    assert isinstance(gen, types.GeneratorType), "must be a generator, not a list"
    print("✓ test_attack_stream_lazy passed")

def test_agent_run_cleanup():
    # cleanup must run even when an exception fires inside the block
    cleaned_up = False
    import io, sys

    output = io.StringIO()
    sys.stdout = output
    try:
        with agent_run() as state:
            state["tool_calls"] += 1
            raise ValueError("agent crashed")
    except ValueError:
        pass
    finally:
        sys.stdout = sys.__stdout__

    captured = output.getvalue()
    assert "run started" in captured, "missing start message"
    assert "run finished" in captured, "cleanup did not run after exception!"
    print("✓ test_agent_run_cleanup passed")

def test_agent_run_state():
    with agent_run() as state:
        assert state == {"tool_calls": 0}
        state["tool_calls"] += 3
    # state updated inside block is visible after
    print("✓ test_agent_run_state passed")


if __name__ == "__main__":
    test_counted_decorator()
    test_counted_independent()
    test_attack_stream_filters()
    test_attack_stream_lazy()
    test_agent_run_cleanup()
    test_agent_run_state()
    print("\nAll tests passed.")
