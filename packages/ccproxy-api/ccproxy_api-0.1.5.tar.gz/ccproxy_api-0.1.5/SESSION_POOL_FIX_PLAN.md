# Session Pool Stale Detection Fix Plan

## Issue Analysis

The session pool incorrectly marks completed streams as "stale" using a fixed 10-second threshold (`idle_seconds > 10.0` in session_pool.py:184). This causes unnecessary interruptions of already-completed streams.

## Root Cause

1. **Incorrect stale detection logic**: Uses 10s timeout instead of proper message-based lifecycle tracking
2. **No stream completion detection**: Pool doesn't detect when streams finish with ResultMessage
3. **Missing first chunk timing**: No distinction between waiting-for-first-chunk vs ongoing streams

## Solution: Message-Based Stream Lifecycle Tracking

### Step 1: Enhance Stream Handle with Message Tracking
- Add message type tracking in `StreamHandle` class
- Track `SystemMessage(init)` reception (first chunk received)
- Track `ResultMessage` reception (stream completed)
- Track timestamps for timeout calculations

### Step 2: Update Session Pool Stale Detection Logic
Replace current logic in `session_pool.py:182-184` with:
```python
# Stream is stale if:
# - No SystemMessage received within 3 seconds (first chunk timeout)
# - SystemMessage received but no activity for 60 seconds (ongoing timeout)
# - Never check stale for completed streams (ResultMessage received)
```

### Step 3: Implementation Details

**In `stream_handle.py`:**
- Add fields: `first_chunk_received_at`, `completed_at`, `has_result_message`
- Track message types in stream worker message processing
- Expose completion status to session pool

**In `session_pool.py`:**
- Update stale detection in `get_session_client()` method (lines 182-184)
- Implement proper timeout logic:
  - 3s timeout if no first chunk
  - 60s timeout if first chunk received but not completed
  - Skip timeout check for completed streams

### Step 4: Message Flow Integration
- Hook into existing message processing in `stream_worker.py`
- Update handle when `SystemMessage(subtype=init)` received
- Update handle when `ResultMessage` received
- No special handling for slash commands (generic solution)

## Files to Modify

1. `ccproxy/claude_sdk/stream_handle.py` - Add message lifecycle tracking
2. `ccproxy/claude_sdk/session_pool.py` - Fix stale detection logic
3. `ccproxy/claude_sdk/stream_worker.py` - Update message tracking in worker

## Testing

- Unit tests for new timeout logic
- Integration tests with slash commands and regular messages
- Verify 3s/60s timeout behavior

## Implementation Order

1. ✅ Write plan to file
2. ✅ Update StreamHandle with message tracking
3. ✅ Update StreamWorker to notify handle of message types
4. ✅ Update SessionPool stale detection logic
5. ✅ Test the fix
6. ✅ Fix Claude SDK client timeout conflict
7. ✅ Fix unhandled StreamTimeoutError exception

## Implementation Summary

The fix has been successfully implemented with the following changes:

### StreamHandle (`ccproxy/claude_sdk/stream_handle.py`)
- Added message lifecycle tracking fields: `_first_chunk_received_at`, `_completed_at`, `_has_result_message`, `_last_activity_at`
- Added methods: `on_first_chunk_received()`, `on_message_received()`, `on_completion()`
- Added properties: `is_completed`, `has_first_chunk`, `idle_seconds`
- Added `is_stale()` method with proper timeout logic:
  - 3s timeout if no SystemMessage received
  - 60s timeout if SystemMessage received but no ResultMessage
  - Never stale for completed streams

### StreamWorker (`ccproxy/claude_sdk/stream_worker.py`)
- Added `stream_handle` parameter to constructor
- Added message tracking logic to notify handle of:
  - All message activity (updates last activity time)
  - SystemMessage with init subtype (first chunk received)
  - ResultMessage (stream completion)

### SessionPool (`ccproxy/claude_sdk/session_pool.py`)
- Replaced fixed 10-second stale detection with message-based timeout logic:
  - First chunk timeout (3s): Terminate session client
  - Ongoing timeout (60s): Interrupt stream but keep session
- Added differentiated timeout handling with proper logging

### ClaudeClient (`ccproxy/claude_sdk/client.py`)
- Modified first chunk timeout handling to check if session pool is enabled
- When session pool is enabled, logs timeout but lets session pool handle cleanup
- When session pool is disabled, maintains original interrupt behavior
- Prevents conflicting timeout handling between client and session pool

### Testing
- All existing unit tests pass
- Type checking passes with mypy
- Linting passes with ruff
- Custom validation tests confirm proper timeout behavior
- Session pool integration tests pass

## Message Flow

```
Stream Start → StreamWorker processes SystemMessage(init) → StreamHandle.on_first_chunk()
Stream Processing → StreamWorker processes content messages → Continue
Stream End → StreamWorker processes ResultMessage → StreamHandle.on_completion()
Session Pool → Check handle.is_completed() before stale detection
```
