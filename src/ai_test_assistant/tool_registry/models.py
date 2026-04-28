from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class ToolStatus(StrEnum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    PLANNED = "planned"
    UNAVAILABLE = "unavailable"


class ToolRiskLevel(StrEnum):
    READ_ONLY = "read_only"
    WRITE_PROJECT_FILES = "write_project_files"
    EXECUTE_LOCAL_COMMAND = "execute_local_command"
    EXTERNAL_NETWORK = "external_network"
    RESTRICTED_ACTION = "restricted_action"


@dataclass(slots=True)
class ToolDefinition:
    name: str
    description: str
    status: ToolStatus
    risk_level: ToolRiskLevel
    category: str
    implementation: str
    notes: str = ""


@dataclass(slots=True)
class ToolExecutionDecision:
    allowed: bool
    requires_confirmation: bool = False
    reasons: list[str] = field(default_factory=list)

