#!/usr/bin/env python3
"""Test ElevenLabs ID validation."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "shared"))

from utils import validate_elevenlabs_id, validate_uuid

# Test cases
test_cases = [
    # (value, id_type, expected_result, description)
    ("agent_8801k2kgsq4kez0twhwr847fcjsn", "agent", True, "Valid agent ID"),
    ("conv_2901k37z3h1vfqbb4a9ak7rn5mjn", "conversation", True, "Valid conversation ID"),
    ("hpzlfkshLu95IeDGtcRS", "document", True, "Valid document ID"),
    ("invalid-format", None, False, "Invalid format"),
    ("550e8400-e29b-41d4-a716-446655440000", None, True, "Standard UUID"),
    ("agent_short", "agent", False, "Agent ID too short"),
    ("conv_toolong12345678901234567890abc", "conversation", False, "Conv ID too long"),
    ("", None, False, "Empty string"),
    (None, None, False, "None value"),
]

print("Testing ElevenLabs ID validation:\n")
print("-" * 60)

passed = 0
failed = 0

for value, id_type, expected, description in test_cases:
    try:
        result = validate_elevenlabs_id(value, id_type)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        if result == expected:
            passed += 1
        else:
            failed += 1
        print(f"{status}: {description}")
        print(f"  Input: {value!r}")
        print(f"  Type: {id_type}")
        print(f"  Expected: {expected}, Got: {result}")
    except Exception as e:
        failed += 1
        print(f"❌ ERROR: {description}")
        print(f"  Input: {value!r}")
        print(f"  Error: {e}")
    print()

print("-" * 60)
print(f"Results: {passed} passed, {failed} failed")
print("✅ All tests passed!" if failed == 0 else f"❌ {failed} tests failed")