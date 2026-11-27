from __future__ import annotations

import re


_COMPLETION_PATTERNS = (r'\bcompleted\b', r'\bfinished\b', r'\bdone\b(?!\s*=\s*false)')

# A response that explicitly negates completion must never be read as a completion
# signal. The positive patterns above match the bare word, so without this guard
# "not done", "not finished" and "done: false" all marked a task complete and made
# the Ralph executor stop early. Negation is checked independently of which
# completion word it attaches to.
_NEGATED_COMPLETION_PATTERNS = (
    r'\bnot\s+(?:yet\s+)?(?:done|complete|completed|finished)\b',
    r"\b(?:isn't|is\s+not|wasn't|was\s+not|hasn't|has\s+not|haven't|have\s+not)\s+(?:been\s+)?(?:done|completed|finished)\b",
    r'\b(?:done|complete|completed|finished)\s*[:=]\s*false\b',
    r'\b(?:incomplete|unfinished|uncompleted)\b',
    r'\bnot\s+yet\b',
)


def _has_negated_completion(lowered: str) -> bool:
    return any(re.search(pattern, lowered) for pattern in _NEGATED_COMPLETION_PATTERNS)


def completion_check(task_text: str, response_text: str, iteration: int, max_iters: int) -> tuple[bool, str]:
    lowered = response_text.lower()
    negated = _has_negated_completion(lowered)
    if not negated and any(re.search(pattern, lowered) for pattern in _COMPLETION_PATTERNS):
        return True, 'response_signals_completion'
    if 'ask user' in lowered:
        return False, 'awaiting_user_input'
    if len(task_text) < 6 and iteration >= 1 and not negated:
        return True, 'short_task_rule'
    return False, 'needs_more_work'
