from enum import Enum


class Action(str, Enum):
    BLOCK = "block"
    FLAG = "flag"
    DISABLED = "disabled"


class PolicyName(str, Enum):
    POLICY_VIOLATION = "policy_violation_detection"
    SECRETS_KEYS = "secrets_keys_detection"
    PII_DETECTION = "pii_detection"
    TOXICITY = "toxicity_detection"
    COMPETITOR_MENTION = "competitor_mention_detection"
    BANNED_TOPICS = "banned_topics_detection"
    PROMPT_INJECTION = "prompt_injection_detection"
    UNSAFE_PROMPT = "unsafe_prompt_protection"
    UNSAFE_RESPONSE = "unsafe_response_detection"
    SYSTEM_PROMPT_LEAK = "system_prompt_leak_detection"


class InteractionType(str, Enum):
    PROMPT = "PROMPT"
    RESPONSE = "RESPONSE"


class Verdict(str, Enum):
    BLOCKED = "blocked"
    FLAGGED = "flagged"
    PASSED = "passed"
