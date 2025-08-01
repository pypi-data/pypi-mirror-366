from __future__ import annotations

import inspect
import uuid
import warnings
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from pydantic import Field, TypeAdapter, ValidationError
from pydantic.types import Annotated

from .enums.core import Action, InteractionType, PolicyName
from .errors import ArgusError, ArgusPermissionError, ArgusTypeError, ArgusValueError
from .internal.http_client import PLAYGROUND_BASE_URL, RUNTIME_SEC_BASE_URL, HttpClient
from .internal.validation import arg_validator, format_policy_error
from .tracing import context as trace_context
from .tracing.tracer import Tracer
from .tracing.types import NodeSubTypeEnum, NodeTypeEnum
from .types.core import ApiResult, Policy, PolicyValue

_API_USER_DEFAULT_ASSET = "api-user-default"


_POLICY_CONFIG_REQUIREMENTS: Dict[PolicyName, Tuple[str, bool, Type]] = {
    PolicyName.POLICY_VIOLATION: ("rules", False, List[str]),
    PolicyName.COMPETITOR_MENTION: ("competitors", False, List[str]),
    PolicyName.BANNED_TOPICS: ("topics", False, List[str]),
    PolicyName.SYSTEM_PROMPT_LEAK: ("system_prompt", False, str),
    PolicyName.SECRETS_KEYS: ("patterns", True, List[Tuple[str, str]]),
}


class ArgusClient:
    """
    ... (docstring is unchanged)
    """

    def __init__(
        self,
        api_key: str,
        http_client: HttpClient,
        access_level: int,
        asset_id: Optional[str] = None,
        session_id: Optional[str] = None,
        policy: Optional[Policy] = None,
        save: bool = False,
        strict: bool = True,
    ):
        self._api_key = api_key
        self._http_client = http_client
        self._access_level = access_level
        self._is_platform_user = self._access_level == 2
        self._asset_id = asset_id
        self._session_id = session_id
        self._strict = strict

        self._policy: Policy = self._create_default_policy_state()
        if policy:
            self.set_policies(policy)

        if self._is_platform_user:
            self._save = save
            if self._asset_id:
                self._http_client.verify_asset(self._asset_id)
            self.tracer = Tracer(
                http_client=self._http_client,
                default_asset_id=self._asset_id,
                default_save=self._save,
            )
        else:
            if asset_id:
                warnings.warn(
                    "The 'asset_id' parameter is ignored for free plan users.",
                    UserWarning,
                    stacklevel=2,
                )
            if session_id:
                warnings.warn(
                    "The 'session_id' parameter is ignored for free plan users.",
                    UserWarning,
                    stacklevel=2,
                )
            if save:
                warnings.warn(
                    "The 'save' parameter is ignored for free plan users.",
                    UserWarning,
                    stacklevel=2,
                )
            self._asset_id, self._session_id, self._save = None, None, False

    @classmethod
    @arg_validator
    def create(
        cls,
        api_key: Annotated[str, Field(min_length=1)],
        url: Optional[str] = None,
        asset_id: Optional[str] = None,
        session_id: Optional[str] = None,
        policy: Optional[Policy] = None,
        save: bool = False,
        strict: bool = True,
    ) -> "ArgusClient":

        if url:
            if not url.startswith(("http://", "https://")):
                raise ArgusValueError("URL must start with 'http://' or 'https://'.")
            base_url = url
        elif api_key.startswith("sk_"):
            base_url = PLAYGROUND_BASE_URL
        elif api_key.startswith("rsk_"):
            base_url = RUNTIME_SEC_BASE_URL
        else:
            raise ArgusValueError(
                "Invalid API key format. Key must start with 'rsk_' or 'sk_'."
            )

        http_client = HttpClient(api_key=api_key, base_url=base_url)
        access_level = http_client.verify_api_key()
        return cls(
            api_key=api_key,
            http_client=http_client,
            access_level=access_level,
            asset_id=asset_id,
            session_id=session_id,
            policy=policy,
            save=save,
            strict=strict,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._http_client.close()

    def _handle_error(
        self, message: str, exception_type: Type[ArgusError] = ArgusValueError
    ):
        if self._strict:
            raise exception_type(message)
        else:
            warnings.warn(message, UserWarning, stacklevel=2)

    def _format_policy_for_api(
        self, policy_dict: Optional[Policy]
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Transforms the internal policy dictionary format to the list format
        expected by the API endpoint.
        """
        if not policy_dict:
            return None
        formatted_policies = []
        for policy_name, config in policy_dict.items():
            action = config.get("action")
            if not action:
                continue

            metadata_key, _, _ = _POLICY_CONFIG_REQUIREMENTS.get(
                policy_name, (None, None, None)
            )

            new_policy_entry = {
                "policy_name": policy_name.value,
                "action": action.value,
                "metadata": config.get(metadata_key, "") if metadata_key else "",
            }
            formatted_policies.append(new_policy_entry)
        return formatted_policies

    def _create_default_policy_state(self) -> Policy:

        return {pn: {"action": Action.DISABLED} for pn in PolicyName}

    def _validate_provided_policy(self, policy: Policy):
        for policy_name, config in policy.items():
            if not isinstance(config, dict) or "action" not in config:
                raise ArgusValueError(
                    f"Invalid config for policy '{policy_name.value}'. Must be a dict with an 'action' key."
                )

            if config.get("action") != Action.DISABLED:
                if policy_name in _POLICY_CONFIG_REQUIREMENTS:
                    required_key, allow_empty, expected_type = (
                        _POLICY_CONFIG_REQUIREMENTS[policy_name]
                    )

                    if required_key not in config:
                        raise ArgusValueError(
                            f"Policy '{policy_name.value}' is enabled but is missing required key: '{required_key}'."
                        )

                    config_value = config[required_key]

                    try:
                        TypeAdapter(expected_type).validate_python(
                            config_value, strict=True
                        )
                    except ValidationError as e:
                        error = format_policy_error(
                            e, base_key=required_key, policy_name=policy_name.value
                        )
                        raise ArgusTypeError(error) from e

                    if (
                        not allow_empty
                        and isinstance(config_value, list)
                        and not config_value
                    ):
                        self._handle_error(
                            f"Policy '{policy_name.value}' is enabled but the required list '{required_key}' is empty."
                        )

    # todo -> add metadata here
    def _execute_scan(
        self,
        text: str,
        interaction_type: InteractionType,
        policy_override: Optional[Policy] = None,
        asset_id_override: Optional[str] = None,
        session_id_override: Optional[str] = None,
        save_override: Optional[bool] = None,
    ) -> ApiResult:
        effective_policy = (
            policy_override if policy_override is not None else self._policy
        )
        has_active_client_policy = any(
            p.get("action") != Action.DISABLED for p in effective_policy.values()
        )

        asset_id = (
            asset_id_override if asset_id_override is not None else self._asset_id
        )
        save = save_override if save_override is not None else self._save

        if has_active_client_policy:
            self._validate_provided_policy(effective_policy)

        if self._is_platform_user:
            if not asset_id and save:
                raise ArgusValueError(
                    "An 'asset_id' must be provided for saving records."
                )
        else:
            if not has_active_client_policy:
                raise ArgusValueError(
                    "API users must provide at least one active policy. Use set_policies() or pass a 'policy' override."
                )

        formatted_policy = self._format_policy_for_api(effective_policy)

        if self._is_platform_user:
            return self.tracer.run_guardrail_check(
                content=text,
                node_subtype=interaction_type,
                name="Content Guardrails",
                asset_id=asset_id,
                session_id=session_id_override,
                save=save,
                policies=formatted_policy,
            )
        else:
            return self._http_client.post_scan(
                text=text,
                interaction_type=interaction_type,
                policy=formatted_policy,
                asset_id=_API_USER_DEFAULT_ASSET,
                session_id=None,
                save=False,
            )

    def _check_specific_policy(
        self,
        policy_name: PolicyName,
        text: str,
        interaction_type: InteractionType,
        action: Action,
        config_data: Optional[Dict[str, Any]] = None,
        **overrides,
    ) -> ApiResult:
        policy_override = self._create_default_policy_state()
        policy_config: PolicyValue = {"action": action}
        if config_data:
            policy_config.update(config_data)

        policy_override[policy_name] = policy_config

        return self._execute_scan(
            text=text,
            interaction_type=interaction_type,
            policy_override=policy_override,
            asset_id_override=overrides.get("asset_id"),
            session_id_override=overrides.get("session_id"),
            save_override=overrides.get("save"),
        )

    @contextmanager
    def trace_context(self, trace_id: Optional[str] = None):
        if trace_context.get_trace_id():
            yield
            return

        active_trace_id = trace_id or str(uuid.uuid4())
        trace_context.set_trace_id(active_trace_id)
        try:
            yield
        finally:
            trace_context.clear_trace_context()

    def _guard_decorator_factory(
        self,
        node_type: NodeTypeEnum,
        node_subtype: NodeSubTypeEnum,
        name: Optional[str] = None,
        check_input_args: Optional[List[str]] = None,
        check_output: bool = True,
        policies: Optional[Policy] = None,
        session_id: Optional[str] = None,
        node_metadata: Optional[Dict[str, Any]] = None,
    ):
        """Factory to create the guard decorators."""

        def decorator(func: Callable):
            sig = inspect.signature(func)
            func_name = name or func.__name__

            def run_input_checks(bound_args):
                """Helper to check specified input arguments."""
                if not check_input_args:
                    return
                for arg_name in check_input_args:
                    if arg_name in bound_args.arguments:
                        content_to_check = str(bound_args.arguments[arg_name])
                        self.check_content(
                            content=content_to_check,
                            node_subtype=NodeSubTypeEnum.GUARDRAILS,
                            name=f"Input Check: '{arg_name}' for {func_name}",
                            policies=policies,
                            session_id=(
                                session_id
                                if session_id is not None
                                else self._session_id
                            ),
                        )

            def run_output_check(result):
                """Helper to check the function's output."""
                if not check_output or result is None:
                    return
                content_to_check = str(result)
                self.check_content(
                    content=content_to_check,
                    node_subtype=NodeSubTypeEnum.GUARDRAILS,
                    name=f"Output Check for {func_name}",
                    policies=policies,
                    session_id=(
                        session_id if session_id is not None else self._session_id
                    ),
                )

            # --- Wrapper for standard SYNC functions ---
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                metadata = node_metadata or {}

                with self.tracer.start_span(
                    name=func_name,
                    node_type=node_type,
                    node_subtype=node_subtype,
                    session_id=(
                        session_id if session_id is not None else self._session_id
                    ),
                    node_metadata=metadata,
                ):
                    bound_args = sig.bind(*args, **kwargs)
                    bound_args.apply_defaults()
                    run_input_checks(bound_args)

                    result = func(*args, **kwargs)

                    run_output_check(result)
                    return result

            # --- Wrapper for ASYNC functions ---
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                metadata = node_metadata or {}

                with self.tracer.start_span(
                    name=func_name,
                    node_type=node_type,
                    session_id=(
                        session_id if session_id is not None else self._session_id
                    ),
                    node_metadata=metadata,
                    node_subtype=node_subtype,
                ):
                    bound_args = sig.bind(*args, **kwargs)
                    bound_args.apply_defaults()
                    run_input_checks(bound_args)

                    result = await func(*args, **kwargs)

                    run_output_check(result)
                    return result

            if inspect.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper

        return decorator

    def guard_entrypoint(
        self,
        name: Optional[str] = None,
        node_subtype: Optional[NodeSubTypeEnum] = None,
        check_input_args: Optional[List[str]] = None,
        check_output: bool = True,
        session_id: Optional[str] = None,
        node_metadata: Optional[Dict[str, Any]] = None,
    ):
        """Decorator to guard the primary entry point of a workflow."""
        return self._guard_decorator_factory(
            node_type=NodeTypeEnum.ORCHESTRATOR,
            node_subtype=(
                NodeSubTypeEnum(node_subtype)
                if node_subtype
                else NodeSubTypeEnum.ORCHESTRATOR
            ),
            name=name,
            check_input_args=check_input_args,
            check_output=check_output,
            session_id=session_id,
            node_metadata=node_metadata,
        )

    def guard_agent(
        self,
        name: Optional[str] = None,
        node_subtype: Optional[NodeSubTypeEnum] = None,
        check_input_args: Optional[List[str]] = None,
        check_output: bool = False,
        session_id: Optional[str] = None,
        node_metadata: Optional[Dict[str, Any]] = None,
    ):
        """Decorator to guard and observe a main agent component."""
        return self._guard_decorator_factory(
            node_type=NodeTypeEnum.AGENT,
            node_subtype=(
                NodeSubTypeEnum(node_subtype) if node_subtype else NodeSubTypeEnum.AGENT
            ),
            name=name,
            check_input_args=check_input_args,
            check_output=check_output,
            session_id=session_id,
            node_metadata=node_metadata,
        )

    def guard_tool(
        self,
        name: Optional[str] = None,
        node_subtype: Optional[NodeSubTypeEnum] = None,
        check_input_args: Optional[List[str]] = None,
        check_output: bool = True,
        policies: Optional[Policy] = None,
        session_id: Optional[str] = None,
        node_metadata: Optional[Dict[str, Any]] = None,
    ):
        """Decorator to guard a tool, applying security policies to its I/O."""
        return self._guard_decorator_factory(
            node_type=NodeTypeEnum.TOOL,
            node_subtype=(
                NodeSubTypeEnum(node_subtype) if node_subtype else NodeSubTypeEnum.TOOL
            ),
            name=name,
            check_input_args=check_input_args,
            check_output=check_output,
            policies=policies,
            session_id=session_id,
            node_metadata=node_metadata,
        )

    def guard_database(self, name: Optional[str] = None, **kwargs):
        """Alias for `guard_tool` for database interactions."""
        return self.guard_tool(
            name=name, node_subtype=NodeSubTypeEnum.DATABASE, **kwargs
        )

    def guard_knowledge_base(self, name: Optional[str] = None, **kwargs):
        """Alias for `guard_tool` for knowledge base (RAG) lookups."""
        return self.guard_tool(
            name=name, node_subtype=NodeSubTypeEnum.KNOWLEDGE_BASE, **kwargs
        )

    def guard_model_generation(self, name: Optional[str] = None, **kwargs):
        """Alias for `guard_tool` for LLM generation calls."""
        return self.guard_tool(name=name, node_subtype=NodeSubTypeEnum.MODEL, **kwargs)

    def guard_mcp_client(self, name: Optional[str] = None, **kwargs):
        """Alias for `guard_agent` for MCP client interactions."""
        return self.guard_agent(
            name=name, node_subtype=NodeSubTypeEnum.MCP_CLIENT, **kwargs
        )

    def guard_mcp_server(self, name: Optional[str] = None, **kwargs):
        """Alias for `guard_entrypoint` for MCP server interactions."""
        return self.guard_entrypoint(
            name=name, node_subtype=NodeSubTypeEnum.MCP_SERVER, **kwargs
        )

    @arg_validator
    def check_content(
        self,
        content: str,
        node_subtype: Optional[NodeSubTypeEnum] = None,
        *,
        name: str = None,
        policies: Optional[Policy] = None,
        session_id: Optional[str] = None,
        node_metadata: Optional[Dict[str, Any]] = None,
        save: Optional[bool] = None,
    ) -> ApiResult:
        effective_policies = self._format_policy_for_api(
            policies or self.get_enabled_policies()
        )

        return self.tracer.run_guardrail_check(
            content=content,
            name=name if name else "Policy Validation",
            policies=effective_policies,
            session_id=session_id if session_id is not None else self._session_id,
            save=save,
            node_metadata=node_metadata,
            node_subtype=(
                node_subtype if node_subtype is not None else NodeSubTypeEnum.GUARDRAILS
            ),
        )

    @arg_validator
    def check_prompt(
        self,
        prompt: str,
        *,
        policy: Optional[Policy] = None,
        asset_id: Optional[str] = None,
        session_id: Optional[str] = None,
        save: Optional[bool] = None,
    ) -> ApiResult:
        return self._execute_scan(
            text=prompt,
            interaction_type=InteractionType.PROMPT,
            policy_override=policy,
            asset_id_override=asset_id,
            session_id_override=session_id,
            save_override=save,
        )

    @arg_validator
    def check_response(
        self,
        response: str,
        *,
        policy: Optional[Policy] = None,
        asset_id: Optional[str] = None,
        session_id: Optional[str] = None,
        save: Optional[bool] = None,
    ) -> ApiResult:
        return self._execute_scan(
            text=response,
            interaction_type=InteractionType.RESPONSE,
            policy_override=policy,
            asset_id_override=asset_id,
            session_id_override=session_id,
            save_override=save,
        )

    @arg_validator
    def check_policy_violation(
        self,
        text: str,
        interaction_type: InteractionType,
        action: Action,
        rules: List[str],
        **kwargs,
    ) -> ApiResult:
        return self._check_specific_policy(
            PolicyName.POLICY_VIOLATION,
            text,
            interaction_type,
            action,
            {"rules": rules},
            **kwargs,
        )

    @arg_validator
    def check_secrets_keys(
        self,
        text: str,
        action: Action,
        patterns: Optional[List[Tuple[str, str]]] = None,
        **kwargs,
    ) -> ApiResult:
        return self._check_specific_policy(
            PolicyName.SECRETS_KEYS,
            text,
            InteractionType.RESPONSE,
            action,
            {"patterns": patterns or []},
            **kwargs,
        )

    @arg_validator
    def check_pii(
        self, text: str, interaction_type: InteractionType, action: Action, **kwargs
    ) -> ApiResult:
        return self._check_specific_policy(
            PolicyName.PII_DETECTION, text, interaction_type, action, **kwargs
        )

    @arg_validator
    def check_toxicity(
        self, text: str, interaction_type: InteractionType, action: Action, **kwargs
    ) -> ApiResult:
        return self._check_specific_policy(
            PolicyName.TOXICITY, text, interaction_type, action, **kwargs
        )

    @arg_validator
    def check_competitor_mention(
        self,
        text: str,
        interaction_type: InteractionType,
        action: Action,
        competitors: List[str],
        **kwargs,
    ) -> ApiResult:
        return self._check_specific_policy(
            PolicyName.COMPETITOR_MENTION,
            text,
            interaction_type,
            action,
            {"competitors": competitors},
            **kwargs,
        )

    @arg_validator
    def check_banned_topics(
        self, prompt: str, action: Action, topics: List[str], **kwargs
    ) -> ApiResult:
        return self._check_specific_policy(
            PolicyName.BANNED_TOPICS,
            prompt,
            InteractionType.PROMPT,
            action,
            {"topics": topics},
            **kwargs,
        )

    @arg_validator
    def check_prompt_injection(
        self, prompt: str, action: Action, **kwargs
    ) -> ApiResult:
        return self._check_specific_policy(
            PolicyName.PROMPT_INJECTION,
            prompt,
            InteractionType.PROMPT,
            action,
            **kwargs,
        )

    @arg_validator
    def check_unsafe_prompt(self, prompt: str, action: Action, **kwargs) -> ApiResult:
        return self._check_specific_policy(
            PolicyName.UNSAFE_PROMPT, prompt, InteractionType.PROMPT, action, **kwargs
        )

    @arg_validator
    def check_unsafe_response(self, text: str, action: Action, **kwargs) -> ApiResult:
        return self._check_specific_policy(
            PolicyName.UNSAFE_RESPONSE, text, InteractionType.RESPONSE, action, **kwargs
        )

    @arg_validator
    def check_system_prompt_leak(
        self, text: str, action: Action, system_prompt: str, **kwargs
    ) -> ApiResult:
        return self._check_specific_policy(
            PolicyName.SYSTEM_PROMPT_LEAK,
            text,
            InteractionType.RESPONSE,
            action,
            {"system_prompt": system_prompt},
            **kwargs,
        )

    @arg_validator
    def set_asset_id(self, asset_id: str):
        if not self._is_platform_user:
            self._handle_error(
                "set_asset_id is only available for Platform users.",
                ArgusPermissionError,
            )
            return
        self._http_client.verify_asset(asset_id)
        self._asset_id = asset_id

    @arg_validator
    def get_asset_id(self) -> Optional[str]:
        if not self._is_platform_user:
            self._handle_error(
                "get_asset_id is only available for Platform users.",
                ArgusPermissionError,
            )
            return None
        return self._asset_id

    @arg_validator
    def clear_asset_id(self):
        if not self._is_platform_user:
            self._handle_error(
                "clear_asset_id is only available for Platform users.",
                ArgusPermissionError,
            )
            return
        self._asset_id = None

    @arg_validator
    def set_session_id(self, session_id: str):
        if not self._is_platform_user:
            self._handle_error(
                "set_session_id is only available for Platform users.",
                ArgusPermissionError,
            )
            return
        self._session_id = session_id

    @arg_validator
    def get_session_id(self) -> Optional[str]:
        if not self._is_platform_user:
            self._handle_error(
                "get_session_id is only available for Platform users.",
                ArgusPermissionError,
            )
            return None
        return self._session_id

    @arg_validator
    def clear_session_id(self):
        if not self._is_platform_user:
            self._handle_error(
                "clear_session_id is only available for Platform users.",
                ArgusPermissionError,
            )
            return
        self._session_id = None

    @arg_validator
    def set_policies(self, policies_to_set: Policy):
        self._validate_provided_policy(policies_to_set)
        self._policy.update(policies_to_set)

    @arg_validator
    def get_enabled_policies(self) -> Policy:
        return {
            k: v for k, v in self._policy.items() if v.get("action") != Action.DISABLED
        }

    @arg_validator
    def clear_policies(self):
        self._policy = self._create_default_policy_state()

    def close(self):
        self._http_client.close()
