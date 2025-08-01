import uuid
from contextlib import contextmanager
from typing import Any, Dict, Generator, Optional

from ..internal.http_client import HttpClient
from ..types.core import ApiResult, Policy
from . import context as trace_context
from .types import NodeSubTypeEnum, NodeTypeEnum


class Tracer:
    """
    Class that manages the creation and reporting of trace events.
    """

    def __init__(
        self,
        http_client: HttpClient,
        default_asset_id: Optional[str],
        default_save: bool,
    ):
        self._http_client = http_client
        self._default_asset_id = default_asset_id
        self._default_save = default_save

    @contextmanager
    def start_span(
        self,
        *,
        name: str,
        node_type: NodeTypeEnum,
        node_subtype: NodeSubTypeEnum,
        session_id: Optional[str] = None,
        asset_id: Optional[str] = None,
        save: Optional[bool] = None,
        node_metadata: Optional[Dict[str, Any]] = None,
    ) -> Generator[None, None, None]:
        """
        Starts a new span, records a visibility-only event, and manages context.
        """
        parent_span_id = trace_context.get_current_span_id()
        trace_id = trace_context.get_trace_id()

        if not trace_id:
            trace_id = str(uuid.uuid4())
            trace_context.set_trace_id(trace_id)

        span_id = str(uuid.uuid4())

        payload = {
            "asset_id": asset_id if asset_id is not None else self._default_asset_id,
            "save": save if save is not None else self._default_save,
            "node": {
                "node_name": name,
                "node_type": node_type.value,
                "node_metadata": node_metadata,
                "node_subtype": node_subtype.value,
            },
            "trace": {
                "trace_id": trace_id,
                "span_id": span_id,
                "parent_span_id": parent_span_id,
            },
            "session_id": session_id,
        }

        self._http_client.post_event(payload)

        try:
            trace_context.push_span_id(span_id)
            yield
        finally:
            trace_context.pop_span_id()

    def run_guardrail_check(
        self,
        *,
        content: str,
        node_subtype: NodeSubTypeEnum,
        name: str,
        policies: Optional[Policy],
        session_id: Optional[str] = None,
        asset_id: Optional[str] = None,
        save: Optional[bool] = None,
        node_metadata: Optional[Dict[str, Any]] = None,
    ) -> ApiResult:
        """
        Runs a full guardrail check, creating both a guardrail node and its evaluation.
        """
        parent_span_id = trace_context.get_current_span_id()
        trace_id = trace_context.get_trace_id()

        if not trace_id:
            trace_id = str(uuid.uuid4())
            trace_context.set_trace_id(trace_id)

        span_id = str(uuid.uuid4())

        payload = {
            "asset_id": asset_id if asset_id is not None else self._default_asset_id,
            "save": save if save is not None else self._default_save,
            "node": {
                "node_name": name,
                "node_type": NodeTypeEnum.GUARDRAILS.value,
                "node_metadata": node_metadata,
                "node_subtype": node_subtype.value,
            },
            "trace": {
                "trace_id": trace_id,
                "span_id": span_id,
                "parent_span_id": parent_span_id,
            },
            "session_id": session_id,
            "evaluation": {"content": content, "policies": policies},
        }

        return self._http_client.post_event(payload)
