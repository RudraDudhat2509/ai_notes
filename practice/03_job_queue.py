"""
EXERCISE 03 — IN-MEMORY JOB QUEUE
===================================
Before using Redis Streams in production, understand the mechanics
by building a simple job queue in pure Python.

This is the pattern behind every async task system:
Celery, Redis Streams, SQS, BullMQ — all the same idea underneath.

SYSTEM DESIGN CONTEXT:
  WhatsApp webhook arrives → push job to queue → return 200 immediately
  Background worker → pull job → process → mark done

YOUR TASK: implement JobQueue with three methods.

HOW IT WORKS:
  - enqueue()  → add a job to the back of the queue
  - dequeue()  → take a job from the front (blocks if empty, up to timeout)
  - complete() → mark a job as done (removes from in-progress tracking)

  If a worker crashes before calling complete(), the job stays in
  in_progress and can be reclaimed. This is the same guarantee
  Redis Streams gives you with xack.

RULES:
  - Use only: collections.deque, threading.Lock, threading.Event, time, uuid
  - No asyncio for this one — use threading primitives
"""

import time
import uuid
from collections import deque
from threading import Lock, Event


class JobQueue:
    def __init__(self):
        self.queue = deque()          # pending jobs
        self.in_progress = {}         # job_id → job, for crash recovery
        self.lock = Lock()            # thread safety
        self._job_available = Event() # signals workers that a job arrived

    def enqueue(self, job: dict) -> str:
        """
        Add a job to the queue.
        Assign it a unique job_id (use str(uuid.uuid4())).
        Store job_id inside the job dict.
        Returns the job_id.

        YOU IMPLEMENT THIS.
        """
            
        job_id = str(uuid.uuid4())
        job["job_id"] = job_id
        with self.lock:
            self.queue.append(job)
            self._job_available.set()
        return job_id


    def dequeue(self, timeout: float = 5.0) -> dict | None:
        """
        Take the next job from the front of the queue.
        Move it to in_progress so we can track it.
        If queue is empty, wait up to `timeout` seconds for a job.
        If still empty after timeout, return None.

        YOU IMPLEMENT THIS.
        """
        deadline = time.time() + timeout
        while True:
            with self.lock:
                if self.queue:
                    job = self.queue.popleft()
                    self.in_progress[job["job_id"]] = (job, time.time())
                    return job
                self._job_available.clear()

            remaining = deadline - time.time()
            if remaining <= 0:
                return None
            self._job_available.wait(timeout=remaining)
            

    def complete(self, job_id: str) -> None:
        with self.lock:
            self.in_progress.pop(job_id, None)
        

    def get_stuck_jobs(self, older_than_seconds: float = 30.0) -> list:
        """
        Return jobs that have been in_progress for longer than older_than_seconds.
        These are likely from crashed workers and should be re-queued.

        ALREADY IMPLEMENTED — read this to understand the in_progress structure.
        """
        now = time.time()
        stuck = []
        with self.lock:
            for job_id, (job, started_at) in self.in_progress.items():
                if now - started_at > older_than_seconds:
                    stuck.append(job)
        return stuck


# ── TESTS ── do not modify below this line ──────────────────────────────────

def test_enqueue_dequeue():
    q = JobQueue()
    job_id = q.enqueue({"task": "send_report", "client": "altagic-001"})
    assert job_id is not None
    job = q.dequeue(timeout=1.0)
    assert job is not None
    assert job["task"] == "send_report"
    assert job["job_id"] == job_id
    print("✓ test_enqueue_dequeue passed")

def test_empty_queue_returns_none():
    q = JobQueue()
    result = q.dequeue(timeout=0.2)   # nothing in queue, should return None quickly
    assert result is None
    print("✓ test_empty_queue_returns_none passed")

def test_complete_removes_from_in_progress():
    q = JobQueue()
    job_id = q.enqueue({"task": "fetch_shopify"})
    job = q.dequeue(timeout=1.0)
    assert job_id in q.in_progress       # should be tracked while in progress
    q.complete(job_id)
    assert job_id not in q.in_progress   # should be gone after complete
    print("✓ test_complete_removes_from_in_progress passed")

def test_crash_recovery():
    q = JobQueue()
    q.enqueue({"task": "fetch_meta"})
    job = q.dequeue(timeout=1.0)
    # worker "crashes" — never calls complete()
    # job should still be in in_progress
    assert job["job_id"] in q.in_progress
    print("✓ test_crash_recovery passed")

def test_fifo_order():
    q = JobQueue()
    q.enqueue({"task": "first"})
    q.enqueue({"task": "second"})
    q.enqueue({"task": "third"})
    assert q.dequeue(timeout=1.0)["task"] == "first"
    assert q.dequeue(timeout=1.0)["task"] == "second"
    assert q.dequeue(timeout=1.0)["task"] == "third"
    print("✓ test_fifo_order passed")

if __name__ == "__main__":
    test_enqueue_dequeue()
    test_empty_queue_returns_none()
    test_complete_removes_from_in_progress()
    test_crash_recovery()
    test_fifo_order()
    print("\nAll tests passed.")
