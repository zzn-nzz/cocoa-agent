"""
Test function for react-milestone-contributor-analysis.

Evaluates the contributor analysis results for React 16.0 milestone.
"""

import json
import re

# Ground truth values
EXPECTED_ANSWER = {
    "top_contributor": "gaearon",
    "top_contributor_issues": 17,
    "most_discussed_issue": 7311,
    "bug_count": 3
}


def _extract_answer_from_text(text: str) -> str | None:
    """Extract answer from <answer>...</answer> tags."""
    answer_pattern = re.compile(r'<answer>(.*?)</answer>', re.IGNORECASE | re.DOTALL)
    match = answer_pattern.search(text)
    if match:
        return match.group(1).strip()
    return None


def _extract_answer_from_conversation(conversation: list) -> str | None:
    """Extract answer from conversation history."""
    # First, check assistant messages with tool_calls for task_complete with result parameter
    for message in reversed(conversation or []):
        if not isinstance(message, dict):
            continue
        if message.get("role") == "assistant" and message.get("tool_calls"):
            for tc in message.get("tool_calls", []):
                if not isinstance(tc, dict):
                    continue
                func = tc.get("function", {})
                if func.get("name") == "task_complete":
                    try:
                        args_str = func.get("arguments", "{}")
                        args = json.loads(args_str) if isinstance(args_str, str) else args_str
                        if "result" in args:
                            result_str = args["result"]
                            answer = _extract_answer_from_text(result_str)
                            if answer:
                                return answer
                    except (json.JSONDecodeError, Exception):
                        pass

    # Search through assistant messages in reverse order for answer in content
    for message in reversed(conversation or []):
        if not isinstance(message, dict):
            continue
        if message.get("role") != "assistant":
            continue
        content = message.get("content") or ""
        answer = _extract_answer_from_text(content)
        if answer:
            return answer
    return None


def _parse_json_answer(answer: str) -> dict | None:
    """Parse JSON from answer string."""
    try:
        # Try to parse as JSON directly
        return json.loads(answer)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code block
        json_pattern = re.compile(r'```(?:json)?\s*(.*?)\s*```', re.DOTALL)
        match = json_pattern.search(answer)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        return None


def test(result: dict) -> dict:
    """
    Test executor result.

    Args:
        result: Result dict from TaskExecutor.run_task()

    Returns:
        Test dict with metrics and pass/fail status
    """
    conversation = result.get("conversation") or []
    task_completed = result.get("status") == "success"

    # First, check if task_result is directly provided in result dict
    task_result = result.get("task_result")
    output_answer = None
    if task_result:
        output_answer = _extract_answer_from_text(task_result)

    # If not found in task_result, extract from conversation
    if not output_answer:
        output_answer = _extract_answer_from_conversation(conversation)

    if not output_answer:
        return {
            "passed": False,
            "feedback": "No valid answer found. Expected format: <answer>{...}</answer>",
            "details": {
                "task_completed": task_completed,
                "conversation_length": len(conversation),
            },
        }

    # Parse JSON from answer
    parsed_answer = _parse_json_answer(output_answer)

    if parsed_answer is None:
        return {
            "passed": False,
            "feedback": f"Could not parse answer as JSON: {output_answer[:200]}",
            "details": {
                "task_completed": task_completed,
                "output_answer": output_answer,
            },
        }

    # Check each field
    checks = {}

    # Check top_contributor (case-insensitive)
    got_contributor = str(parsed_answer.get("top_contributor", "")).lower()
    expected_contributor = EXPECTED_ANSWER["top_contributor"].lower()
    checks["top_contributor"] = got_contributor == expected_contributor

    # Check top_contributor_issues
    got_issues = parsed_answer.get("top_contributor_issues")
    checks["top_contributor_issues"] = got_issues == EXPECTED_ANSWER["top_contributor_issues"]

    # Check most_discussed_issue
    got_discussed = parsed_answer.get("most_discussed_issue")
    checks["most_discussed_issue"] = got_discussed == EXPECTED_ANSWER["most_discussed_issue"]

    # Check bug_count
    got_bugs = parsed_answer.get("bug_count")
    checks["bug_count"] = got_bugs == EXPECTED_ANSWER["bug_count"]

    all_correct = all(checks.values())
    passed = task_completed and all_correct

    feedback_parts = []
    feedback_parts.append(f"{'✓' if checks['top_contributor'] else '✗'} Top contributor: got '{parsed_answer.get('top_contributor')}', expected '{EXPECTED_ANSWER['top_contributor']}'")
    feedback_parts.append(f"{'✓' if checks['top_contributor_issues'] else '✗'} Top contributor issues: got {got_issues}, expected {EXPECTED_ANSWER['top_contributor_issues']}")
    feedback_parts.append(f"{'✓' if checks['most_discussed_issue'] else '✗'} Most discussed issue: got #{got_discussed}, expected #{EXPECTED_ANSWER['most_discussed_issue']}")
    feedback_parts.append(f"{'✓' if checks['bug_count'] else '✗'} Bug count: got {got_bugs}, expected {EXPECTED_ANSWER['bug_count']}")

    if not task_completed:
        feedback_parts.append("✗ Task status is not success.")

    return {
        "passed": passed,
        "feedback": "\n".join(feedback_parts),
        "details": {
            "task_completed": task_completed,
            "parsed_answer": parsed_answer,
            "expected_answer": EXPECTED_ANSWER,
            "checks": checks,
            "all_correct": all_correct,
        },
    }
