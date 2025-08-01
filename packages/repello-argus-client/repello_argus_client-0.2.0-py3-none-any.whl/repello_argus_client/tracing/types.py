from enum import Enum


class NodeTypeEnum(Enum):
    """
    Represents the abstract type of a node in an agentic workflow.
    """

    ORCHESTRATOR = "ORCHESTRATOR"
    AGENT = "AGENT"
    TOOL = "TOOL"
    GUARDRAILS = "GUARDRAILS"


class NodeSubTypeEnum(Enum):
    """
    Represents the specific subtype of a node in an agentic workflow.
    This is used to provide more granular categorization of nodes.
    """

    ORCHESTRATOR = "ORCHESTRATOR"
    AGENT = "AGENT"
    MODEL = "MODEL"
    TOOL = "TOOL"
    KNOWLEDGE_BASE = "KNOWLEDGE_BASE"
    DATABASE = "DATABASE"
    MCP_CLIENT = "MCP_CLIENT"
    MCP_SERVER = "MCP_SERVER"
    PROMPT = "PROMPT"
    RESPONSE = "RESPONSE"
    GUARDRAILS = "GUARDRAILS"
