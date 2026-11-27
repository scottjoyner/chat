"""R31 hermetic regression: negated completion language must not mark a task done.

All fixtures are synthetic strings; no network, model, DB or audio dependency.
"""
from __future__ import annotations

import pytest

from tts_agent.ralph.completion import completion_check

TASK = 'build the complete report'


@pytest.mark.parametrize(
    'response',
    [
        'Task is not done yet; still working on it.',
        'This is not complete.',
        'This is not completed.',
        'Work is not finished.',
        'Not yet done.',
        'Status: done: false',
        'Status: done = false',
        'Status: done=false',
        'The remaining work is incomplete.',
        'The migration is unfinished.',
        "It hasn't been done.",
        'It is not done.',
        'It was not finished.',
    ],
)
def test_negated_completion_never_signals_done(response: str) -> None:
    done, reason = completion_check(TASK, response, 1, 5)
    assert done is False
    assert reason != 'response_signals_completion'


def test_negation_suppresses_short_task_rule() -> None:
    done, reason = completion_check('x', 'not done yet', 1, 5)
    assert done is False
    assert reason == 'needs_more_work'


@pytest.mark.parametrize(
    'response',
    [
        'Done.',
        'All steps completed successfully.',
        'The render is finished.',
        'done = true',
        'Completed.',
    ],
)
def test_unnegated_completion_still_signals_done(response: str) -> None:
    done, reason = completion_check(TASK, response, 1, 5)
    assert done is True
    assert reason == 'response_signals_completion'


def test_ask_user_reason_preserved_when_negated() -> None:
    done, reason = completion_check(TASK, 'Not done yet; ask user for the missing file.', 1, 5)
    assert done is False
    assert reason == 'awaiting_user_input'


def test_short_task_rule_preserved_without_negation() -> None:
    done, reason = completion_check('x', 'working on it', 1, 5)
    assert done is True
    assert reason == 'short_task_rule'


def test_neutral_response_needs_more_work() -> None:
    done, reason = completion_check(TASK, 'working on it', 0, 5)
    assert done is False
    assert reason == 'needs_more_work'
