"""Cross-layer regression for Codex app-server tool cards in the TUI."""

from types import SimpleNamespace

from agent.codex_runtime import _codex_live_event
from tui_gateway import server


def test_codex_bridge_emits_one_authoritative_tui_tool_lifecycle(monkeypatch):
    sid = "codex-live-events"
    events = []
    monkeypatch.setattr(
        server,
        "_emit",
        lambda event_type, session_id, payload: events.append((
            event_type,
            session_id,
            payload,
        )),
    )
    monkeypatch.setitem(
        server._sessions,
        sid,
        {
            "tool_progress_mode": "all",
            "tool_started_at": {},
            "edit_snapshots": {},
        },
    )
    callbacks = server._agent_cbs(sid)
    agent = SimpleNamespace(
        tool_progress_callback=callbacks["tool_progress_callback"],
        tool_start_callback=callbacks["tool_start_callback"],
        tool_complete_callback=callbacks["tool_complete_callback"],
    )
    started = {
        "type": "commandExecution",
        "id": "tool-1",
        "command": "pwd",
        "cwd": "/tmp",
    }

    _codex_live_event(agent, {"method": "item/started", "params": {"item": started}})
    _codex_live_event(
        agent,
        {
            "method": "item/completed",
            "params": {"item": dict(started, aggregatedOutput="/tmp\n", exitCode=0)},
        },
    )

    assert [event_type for event_type, _, _ in events] == [
        "tool.start",
        "tool.complete",
    ]
    assert events[0][2]["tool_id"] == "codex_exec_tool-1"
    assert events[1][2]["tool_id"] == "codex_exec_tool-1"
