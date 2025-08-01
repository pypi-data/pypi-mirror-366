from typing import Any, Dict, List, Tuple, TypedDict

from repello_argus_client.enums.core import Action, PolicyName


class PolicyConfig(TypedDict):
    action: Action


class BannedTopicsConfig(PolicyConfig):
    topics: List[str]


class SecretsKeysConfig(PolicyConfig):
    patterns: List[Tuple[str, str]]


class CompetitorMentionConfig(PolicyConfig):
    competitors: List[str]


class PolicyViolationConfig(PolicyConfig):
    rules: List[str]


class SystemPromptLeakConfig(PolicyConfig):
    system_prompt: str


PolicyValue = Dict[str, Any]


Policy = Dict[PolicyName, PolicyValue]

Metadata = Dict[str, Any]
ApiResult = Dict[str, Any]
