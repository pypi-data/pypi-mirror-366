from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pytest

from repello_argus_client.client import (
    _API_USER_DEFAULT_ASSET,
    ArgusClient,
)
from repello_argus_client.enums.core import Action, InteractionType, PolicyName
from repello_argus_client.errors import (
    ArgusPermissionError,
    ArgusTypeError,
    ArgusValueError,
)
from repello_argus_client.tracing import context as trace_context
from repello_argus_client.tracing.types import NodeSubTypeEnum, NodeTypeEnum
from repello_argus_client.types.core import Policy


@pytest.fixture(autouse=True)
def clear_context_between_tests():
    trace_context.clear_trace_context()
    yield
    trace_context.clear_trace_context()


@pytest.fixture
def mock_http_client_class(monkeypatch):
    mock_class = MagicMock()
    mock_instance = MagicMock()
    mock_instance.post_scan.return_value = {"status": "pass"}
    mock_instance.post_event.return_value = {"status": "pass"}
    mock_class.return_value = mock_instance
    monkeypatch.setattr("repello_argus_client.client.HttpClient", mock_class)
    return mock_class


@pytest.fixture
def mock_tracer_class(monkeypatch):
    mock_class = MagicMock()
    mock_instance = MagicMock()
    mock_instance.start_span.return_value = contextmanager(lambda: (yield))()
    mock_class.return_value = mock_instance
    monkeypatch.setattr("repello_argus_client.client.Tracer", mock_class)
    return mock_class


class TestArgusClientInitialization:
    def test_create_with_runtime_key(self, mock_http_client_class):
        mock_http_client_class.return_value.verify_api_key.return_value = 2
        client = ArgusClient.create(api_key="rsk_test_key")
        assert client._api_key == "rsk_test_key"
        assert client._is_platform_user
        mock_http_client_class.return_value.verify_api_key.assert_called_once()

    def test_create_with_playground_key(self, mock_http_client_class):
        mock_http_client_class.return_value.verify_api_key.return_value = 1
        client = ArgusClient.create(api_key="sk_test_key")
        assert client._api_key == "sk_test_key"
        assert not client._is_platform_user
        mock_http_client_class.return_value.verify_api_key.assert_called_once()

    def test_create_with_explicit_url(self, mock_http_client_class):
        mock_http_client_class.return_value.verify_api_key.return_value = 2
        url = "http://localhost:8080"
        api_key = "rsk_test_key"
        ArgusClient.create(api_key=api_key, url=url)
        mock_http_client_class.assert_called_with(api_key=api_key, base_url=url)

    def test_create_with_invalid_key_format(self):
        with pytest.raises(ArgusValueError, match="Invalid API key format"):
            ArgusClient.create(api_key="invalid_key")

    def test_create_with_invalid_url_format(self):
        with pytest.raises(ArgusValueError, match="URL must start with"):
            ArgusClient.create(api_key="rsk_test_key", url="invalid-url")

    def test_init_platform_user(self, mock_http_client_class, mock_tracer_class):
        mock_http_client_class.return_value.verify_api_key.return_value = 2
        client = ArgusClient.create(
            api_key="rsk_test_key",
            asset_id="test_asset",
            session_id="test_session",
            save=True,
        )
        assert client._is_platform_user
        assert client._asset_id == "test_asset"
        assert client._session_id == "test_session"
        assert client._save
        mock_http_client_class.return_value.verify_asset.assert_called_once_with(
            "test_asset"
        )
        mock_tracer_class.assert_called_once()

    def test_init_free_user(self, mock_http_client_class):
        mock_http_client_class.return_value.verify_api_key.return_value = 1
        with pytest.warns(UserWarning) as record:
            client = ArgusClient.create(
                api_key="sk_test_key",
                asset_id="test_asset",
                session_id="test_session",
                save=True,
            )
            assert len(record) == 3
            assert "'asset_id' parameter is ignored" in str(record[0].message)
            assert "'session_id' parameter is ignored" in str(record[1].message)
            assert "'save' parameter is ignored" in str(record[2].message)

        assert not client._is_platform_user
        assert client._asset_id is None
        assert client._session_id is None
        assert not client._save
        assert not hasattr(client, "tracer")

    def test_init_with_policy(self, mock_http_client_class):
        mock_http_client_class.return_value.verify_api_key.return_value = 1
        policy: Policy = {
            PolicyName.TOXICITY: {"action": Action.BLOCK},
        }
        client = ArgusClient.create(api_key="sk_test_key", policy=policy)
        assert client.get_enabled_policies() == policy

    def test_context_manager(self, mock_http_client_class):
        mock_http_client_class.return_value.verify_api_key.return_value = 1
        with ArgusClient.create(api_key="sk_test_key") as client:
            assert isinstance(client, ArgusClient)
        mock_http_client_class.return_value.close.assert_called_once()
        client.close()
        assert mock_http_client_class.return_value.close.call_count == 2


class TestClientErrorHandlingAndPolicy:
    @pytest.fixture
    def client(self, mock_http_client_class):
        mock_http_client_class.return_value.verify_api_key.return_value = 1
        return ArgusClient.create(api_key="sk_test_key", strict=True)

    @pytest.fixture
    def non_strict_client(self, mock_http_client_class):
        mock_http_client_class.return_value.verify_api_key.return_value = 1
        return ArgusClient.create(api_key="sk_test_key", strict=False)

    def test_handle_error_strict(self, client):
        with pytest.raises(ArgusPermissionError, match="Test error"):
            client._handle_error("Test error", ArgusPermissionError)

    def test_handle_error_non_strict(self, non_strict_client):
        with pytest.warns(UserWarning, match="Test error"):
            non_strict_client._handle_error("Test error", ArgusValueError)

    def test_validate_provided_policy_success(self, client):
        valid_policy: Policy = {
            PolicyName.BANNED_TOPICS: {
                "action": Action.BLOCK,
                "topics": ["politics"],
            },
            PolicyName.TOXICITY: {"action": Action.DISABLED},
        }
        client._validate_provided_policy(valid_policy)

    def test_validate_policy_invalid_config(self, client):
        with pytest.raises(ArgusTypeError, match="Input should be a valid dictionary"):
            client.set_policies(PolicyName.TOXICITY)

    def test_validate_policy_missing_action(self, client):
        with pytest.raises(
            ArgusValueError, match="Must be a dict with an 'action' key"
        ):
            client.set_policies({PolicyName.BANNED_TOPICS: {"topics": ["news"]}})

    def test_validate_policy_missing_required_key(self, client):
        with pytest.raises(ArgusValueError, match="missing required key: 'topics'"):
            client.set_policies({PolicyName.BANNED_TOPICS: {"action": Action.BLOCK}})

    def test_validate_policy_incorrect_type(self, client):
        with pytest.raises(
            ArgusTypeError,
            match="Invalid structure in policy 'banned_topics_detection'",
        ):
            client.set_policies(
                {
                    PolicyName.BANNED_TOPICS: {
                        "action": Action.BLOCK,
                        "topics": "politics",
                    }
                }
            )

    def test_validate_policy_empty_list_warning(self, non_strict_client):
        with pytest.warns(UserWarning, match="required list 'topics' is empty"):
            non_strict_client.set_policies(
                {PolicyName.BANNED_TOPICS: {"action": Action.BLOCK, "topics": []}}
            )

    def test_format_policy_for_api(self, client):
        """
        Tests that the internal policy dictionary is correctly formatted for API submission.
        """
        policy: Policy = {
            PolicyName.BANNED_TOPICS: {
                "action": Action.BLOCK,
                "topics": ["politics"],
            },
            PolicyName.COMPETITOR_MENTION: {
                "action": Action.FLAG,
                "competitors": ["Coke"],
            },
        }
        client.set_policies(policy)

        formatted = client._format_policy_for_api(client._policy)

        assert len(formatted) == len(PolicyName)

        formatted_map = {p["policy_name"]: p for p in formatted}

        banned_topics_key = PolicyName.BANNED_TOPICS.value
        assert formatted_map[banned_topics_key]["action"] == Action.BLOCK.value
        assert formatted_map[banned_topics_key]["metadata"] == ["politics"]

        competitor_mention_key = PolicyName.COMPETITOR_MENTION.value
        assert formatted_map[competitor_mention_key]["action"] == Action.FLAG.value
        assert formatted_map[competitor_mention_key]["metadata"] == ["Coke"]

        toxicity_key = PolicyName.TOXICITY.value
        assert formatted_map[toxicity_key]["action"] == Action.DISABLED.value
        assert formatted_map[toxicity_key]["metadata"] == ""

    def test_format_policy_for_api_none(self, client):
        assert client._format_policy_for_api(None) is None

    def test_policy_management_flow(self, client):
        assert client.get_enabled_policies() == {}
        policy: Policy = {PolicyName.TOXICITY: {"action": Action.BLOCK}}
        client.set_policies(policy)
        assert client.get_enabled_policies() == policy
        client.clear_policies()
        assert client.get_enabled_policies() == {}


class TestClientScanning:
    @pytest.fixture
    def platform_client(self, mock_http_client_class, mock_tracer_class):
        mock_http_client_class.return_value.verify_api_key.return_value = 2
        mock_tracer_class.return_value.run_guardrail_check.return_value = {
            "status": "pass"
        }
        return ArgusClient.create(
            api_key="rsk_test_key", asset_id="default_asset", save=True
        )

    @pytest.fixture
    def free_client(self, mock_http_client_class):
        mock_http_client_class.return_value.verify_api_key.return_value = 1
        return ArgusClient.create(api_key="sk_test_key")

    def test_execute_scan_platform_user(self, platform_client, mock_tracer_class):
        platform_client._execute_scan(
            text="hello", interaction_type=InteractionType.PROMPT
        )
        mock_tracer_class.return_value.run_guardrail_check.assert_called_once()
        call_args = mock_tracer_class.return_value.run_guardrail_check.call_args[1]
        assert call_args["content"] == "hello"
        assert call_args["node_subtype"] == InteractionType.PROMPT
        assert call_args["asset_id"] == "default_asset"
        assert call_args["save"]

    def test_execute_scan_platform_user_no_asset_with_save(self, platform_client):
        platform_client.clear_asset_id()
        with pytest.raises(
            ArgusValueError, match="An 'asset_id' must be provided for saving records"
        ):
            platform_client._execute_scan(
                text="hello",
                interaction_type=InteractionType.PROMPT,
                save_override=True,
            )

    def test_execute_scan_free_user(self, free_client, mock_http_client_class):
        policy: Policy = {PolicyName.TOXICITY: {"action": Action.BLOCK}}
        free_client._execute_scan(
            text="hello",
            interaction_type=InteractionType.PROMPT,
            policy_override=policy,
        )
        mock_http_client_class.return_value.post_scan.assert_called_once()
        call_args = mock_http_client_class.return_value.post_scan.call_args[1]
        assert call_args["text"] == "hello"
        assert call_args["interaction_type"] == InteractionType.PROMPT
        assert call_args["asset_id"] == _API_USER_DEFAULT_ASSET
        assert not call_args["save"]
        assert call_args["policy"] is not None

    def test_execute_scan_free_user_no_policy(self, free_client):
        with pytest.raises(
            ArgusValueError,
            match="API users must provide at least one active policy",
        ):
            free_client._execute_scan(
                text="hello", interaction_type=InteractionType.PROMPT
            )

    def test_check_prompt(self, free_client, mock_http_client_class):
        policy: Policy = {PolicyName.TOXICITY: {"action": Action.BLOCK}}
        free_client.check_prompt("is this bad?", policy=policy)
        mock_http_client_class.return_value.post_scan.assert_called_once()
        call_args = mock_http_client_class.return_value.post_scan.call_args[1]
        assert call_args["interaction_type"] == InteractionType.PROMPT

    def test_check_response(self, free_client, mock_http_client_class):
        policy: Policy = {PolicyName.TOXICITY: {"action": Action.BLOCK}}
        free_client.check_response("this is a bad response", policy=policy)
        mock_http_client_class.return_value.post_scan.assert_called_once()
        call_args = mock_http_client_class.return_value.post_scan.call_args[1]
        assert call_args["interaction_type"] == InteractionType.RESPONSE

    def test_check_specific_policy(self, free_client, mock_http_client_class):
        free_client.check_banned_topics(
            prompt="what about politics", action=Action.BLOCK, topics=["politics"]
        )
        mock_http_client_class.return_value.post_scan.assert_called_once()
        call_args = mock_http_client_class.return_value.post_scan.call_args[1]

        sent_policies = call_args["policy"]
        assert len(sent_policies) == len(PolicyName)

        banned_topics_policy = next(
            (p for p in sent_policies if p["policy_name"] == "banned_topics_detection"),
            None,
        )
        assert banned_topics_policy is not None
        assert banned_topics_policy["action"] == "block"
        assert banned_topics_policy["metadata"] == ["politics"]

    def test_check_secrets_no_patterns(self, free_client, mock_http_client_class):
        free_client.check_secrets_keys(text="my key is rsk_123", action=Action.BLOCK)
        mock_http_client_class.return_value.post_scan.assert_called_once()
        call_args = mock_http_client_class.return_value.post_scan.call_args[1]

        sent_policies = call_args["policy"]
        assert len(sent_policies) == len(PolicyName)

        secrets_policy = next(
            (p for p in sent_policies if p["policy_name"] == "secrets_keys_detection"),
            None,
        )
        assert secrets_policy is not None
        assert secrets_policy["action"] == "block"
        assert secrets_policy["metadata"] == []


class TestAssetAndSessionManagement:
    @pytest.fixture
    def platform_client(self, mock_http_client_class, mock_tracer_class):
        mock_http_client_class.return_value.verify_api_key.return_value = 2
        return ArgusClient.create(api_key="rsk_test_key")

    @pytest.fixture
    def free_client_strict(self, mock_http_client_class):
        mock_http_client_class.return_value.verify_api_key.return_value = 1
        return ArgusClient.create(api_key="sk_test_key", strict=True)

    @pytest.fixture
    def free_client_non_strict(self, mock_http_client_class):
        mock_http_client_class.return_value.verify_api_key.return_value = 1
        return ArgusClient.create(api_key="sk_test_key", strict=False)

    def test_asset_id_platform(self, platform_client, mock_http_client_class):
        assert platform_client.get_asset_id() is None
        platform_client.set_asset_id("new_asset")
        mock_http_client_class.return_value.verify_asset.assert_called_once_with(
            "new_asset"
        )
        assert platform_client.get_asset_id() == "new_asset"
        platform_client.clear_asset_id()
        assert platform_client.get_asset_id() is None

    def test_asset_id_free_strict(self, free_client_strict):
        with pytest.raises(ArgusPermissionError):
            free_client_strict.set_asset_id("asset")
        with pytest.raises(ArgusPermissionError):
            free_client_strict.get_asset_id()
        with pytest.raises(ArgusPermissionError):
            free_client_strict.clear_asset_id()

    def test_asset_id_free_non_strict(self, free_client_non_strict):
        with pytest.warns(UserWarning):
            free_client_non_strict.set_asset_id("asset")
        with pytest.warns(UserWarning):
            assert free_client_non_strict.get_asset_id() is None
        with pytest.warns(UserWarning):
            free_client_non_strict.clear_asset_id()

    def test_session_id_platform(self, platform_client):
        assert platform_client.get_session_id() is None
        platform_client.set_session_id("new_session")
        assert platform_client.get_session_id() == "new_session"
        platform_client.clear_session_id()
        assert platform_client.get_session_id() is None


class TestDecoratorsAndTracing:
    @pytest.fixture
    def platform_client(self, mock_http_client_class, mock_tracer_class):
        mock_http_client_class.return_value.verify_api_key.return_value = 2
        return ArgusClient.create(api_key="rsk_test_key", session_id="client_session")

    @pytest.fixture
    def mock_check_content(self, monkeypatch):
        mock = MagicMock(return_value={"status": "pass"})
        monkeypatch.setattr(ArgusClient, "check_content", mock)
        return mock

    def test_trace_context_manager(self, platform_client):
        assert trace_context.get_trace_id() is None
        with platform_client.trace_context():
            trace_id = trace_context.get_trace_id()
            assert trace_id is not None
            with platform_client.trace_context():
                assert trace_context.get_trace_id() == trace_id
        assert trace_context.get_trace_id() is None

    def test_guard_decorator_factory_sync(
        self, platform_client, mock_tracer_class, mock_check_content
    ):
        @platform_client.guard_tool(
            name="test_tool",
            check_input_args=["user_input"],
            check_output=True,
            session_id="decorator_session",
            node_metadata={"key": "value"},
        )
        def my_sync_tool(user_input: str, other_arg: int = 5):
            return f"Processed: {user_input}"

        result = my_sync_tool("hello", other_arg=10)
        assert result == "Processed: hello"

        mock_tracer_class.return_value.start_span.assert_called_once()
        span_args = mock_tracer_class.return_value.start_span.call_args[1]
        assert span_args["name"] == "test_tool"
        assert span_args["node_type"] == NodeTypeEnum.TOOL
        assert span_args["session_id"] == "decorator_session"
        assert span_args["node_metadata"] == {"key": "value"}

        assert mock_check_content.call_count == 2
        mock_check_content.assert_any_call(
            content="hello",
            node_subtype=NodeSubTypeEnum.GUARDRAILS,
            name="Input Check: 'user_input' for test_tool",
            policies=None,
            session_id="decorator_session",
        )
        mock_check_content.assert_any_call(
            content="Processed: hello",
            node_subtype=NodeSubTypeEnum.GUARDRAILS,
            name="Output Check for test_tool",
            policies=None,
            session_id="decorator_session",
        )

    @pytest.mark.asyncio
    async def test_guard_decorator_factory_async(
        self, platform_client, mock_tracer_class, mock_check_content
    ):
        @platform_client.guard_agent(
            name="test_agent", check_output=True, check_input_args=["prompt"]
        )
        async def my_async_agent(prompt: str):
            return f"Async result for {prompt}"

        result = await my_async_agent("query")
        assert result == "Async result for query"

        mock_tracer_class.return_value.start_span.assert_called_once()
        span_args = mock_tracer_class.return_value.start_span.call_args[1]
        assert span_args["name"] == "test_agent"
        assert span_args["node_type"] == NodeTypeEnum.AGENT
        assert span_args["session_id"] == "client_session"

        assert mock_check_content.call_count == 2
        mock_check_content.assert_any_call(
            content="query",
            node_subtype=NodeSubTypeEnum.GUARDRAILS,
            name="Input Check: 'prompt' for test_agent",
            policies=None,
            session_id="client_session",
        )
        mock_check_content.assert_any_call(
            content="Async result for query",
            node_subtype=NodeSubTypeEnum.GUARDRAILS,
            name="Output Check for test_agent",
            policies=None,
            session_id="client_session",
        )

    def test_guard_aliases(self, platform_client):
        with patch.object(platform_client, "_guard_decorator_factory") as mock_factory:
            platform_client.guard_entrypoint(name="ep")
            mock_factory.assert_called_with(
                node_type=NodeTypeEnum.ORCHESTRATOR,
                node_subtype=NodeSubTypeEnum.ORCHESTRATOR,
                name="ep",
                check_input_args=None,
                check_output=True,
                session_id=None,
                node_metadata=None,
            )

            platform_client.guard_database(name="db", check_output=False)
            mock_factory.assert_called_with(
                name="db",
                node_subtype=NodeSubTypeEnum.DATABASE,
                node_type=NodeTypeEnum.TOOL,
                check_input_args=None,
                check_output=False,
                policies=None,
                session_id=None,
                node_metadata=None,
            )

            platform_client.guard_mcp_server(name="mcp_s")
            mock_factory.assert_called_with(
                name="mcp_s",
                node_subtype=NodeSubTypeEnum.MCP_SERVER,
                node_type=NodeTypeEnum.ORCHESTRATOR,
                check_input_args=None,
                check_output=True,
                session_id=None,
                node_metadata=None,
            )

    def test_check_content(self, platform_client, mock_tracer_class):

        policy: Policy = {PolicyName.TOXICITY: {"action": Action.BLOCK}}
        platform_client.check_content(
            content="test content",
            name="my_check",
            policies=policy,
            session_id="override_session",
        )

        mock_tracer_class.return_value.run_guardrail_check.assert_called_once()
        call_args = mock_tracer_class.return_value.run_guardrail_check.call_args[1]
        assert call_args["content"] == "test content"
        assert call_args["name"] == "my_check"
        assert call_args["session_id"] == "override_session"

        expected_policies = [
            {"policy_name": "toxicity_detection", "action": "block", "metadata": ""}
        ]
        assert call_args["policies"] == expected_policies


class TestPydanticValidationDecorator:
    @pytest.fixture
    def client(self, mock_http_client_class):
        mock_http_client_class.return_value.verify_api_key.return_value = 1
        return ArgusClient.create(api_key="sk_test_key")

    def test_arg_validator_failure(self, client):
        with pytest.raises(
            ArgusTypeError, match="Invalid argument type\\(s\\) provided"
        ):

            client.set_asset_id(12345)

    def test_arg_validator_on_create_method(self):

        with pytest.raises(
            ArgusTypeError, match="Invalid argument type\\(s\\) provided"
        ):
            ArgusClient.create(api_key="rsk_test", asset_id=123)
