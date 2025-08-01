from contextvars import ContextVar
from typing import List, Optional

_trace_id_cv: ContextVar[Optional[str]] = ContextVar("argus_trace_id", default=None)
_span_id_stack_cv: ContextVar[Optional[List[str]]] = ContextVar(
    "argus_span_id_stack", default=None
)


def get_trace_id() -> Optional[str]:
    """Gets the ID of the current execution trace."""
    return _trace_id_cv.get()


def set_trace_id(trace_id: str) -> None:
    """Sets the ID for the current execution trace."""
    _trace_id_cv.set(trace_id)


def get_current_span_id() -> Optional[str]:
    """Gets the ID of the current parent span from the top of the stack."""
    stack = _span_id_stack_cv.get()
    return stack[-1] if stack else None


def push_span_id(span_id: str) -> None:
    """Pushes a new span ID onto the context stack."""
    stack = _span_id_stack_cv.get()
    if stack is None:
        stack = []
    else:
        stack = stack.copy()
    stack.append(span_id)
    _span_id_stack_cv.set(stack)


def pop_span_id() -> Optional[str]:
    """Pops a span ID from the context stack."""
    stack = _span_id_stack_cv.get()
    if not stack:
        return None
    stack = stack.copy()
    popped = stack.pop()
    _span_id_stack_cv.set(stack)
    return popped


def clear_trace_context() -> None:
    """Resets the trace and span context, typically after a trace is complete."""
    _trace_id_cv.set(None)
    _span_id_stack_cv.set([])
