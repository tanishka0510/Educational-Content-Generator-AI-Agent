"""
==========================================================
Orchestrator Agent Constants

Project:
Educational Content Generator AI

Module:
Orchestrator Agent

Purpose:
Defines all immutable constants and enumerations used
throughout the Orchestrator Agent.

Author:
Team Orchestrator
==========================================================
"""

from enum import Enum


# ==========================================================
# User Intents
# ==========================================================

class Intent(str, Enum):
    """Supported user intents."""

    UPLOAD = "upload"
    QA = "qa"
    SUMMARY = "summary"
    QUIZ = "quiz"
    FLASHCARDS = "flashcards"
    LEARNING_OBJECTIVES = "learning_objectives"
    RESOURCE_SEARCH = "resource_search"
    COMPARE = "compare"
    EXPLANATION = "explanation"
    PROGRAMMING = "programming"
    MATHEMATICS = "mathematics"
    ASSIGNMENT = "assignment"
    STUDY_PLAN = "study_plan"
    MULTIMEDIA = "multimedia"
    MIXED_QUERY = "mixed_query"
    FOLLOW_UP = "follow_up"
    GENERAL_KNOWLEDGE = "general_knowledge"
    ADMIN = "admin"


# ==========================================================
# Workflow Categories
# ==========================================================

class WorkflowCategory(str, Enum):
    """Workflow classification."""

    CONTENT = "content"
    EDUCATIONAL = "educational"
    MULTIMEDIA = "multimedia"
    COMPOSITE = "composite"
    CONTEXT = "context"
    SYSTEM = "system"


# ==========================================================
# Execution Strategies
# ==========================================================

class ExecutionStrategy(str, Enum):
    """Workflow execution strategy."""

    SINGLE = "single"
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONTEXT_BASED = "context_based"


# ==========================================================
# Agent Names
# ==========================================================

class AgentName(str, Enum):
    """Registered agents."""

    ORCHESTRATOR = "orchestrator"
    CONTENT_PROCESSING = "content_processing"
    EDUCATIONAL = "educational"
    MULTIMEDIA = "multimedia"


# ==========================================================
# Workflow Status
# ==========================================================

class WorkflowStatus(str, Enum):
    """Workflow lifecycle status."""

    INITIALIZED = "initialized"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ==========================================================
# Response Status
# ==========================================================

class ResponseStatus(str, Enum):
    """API response status."""

    SUCCESS = "success"
    FAILURE = "failure"


# ==========================================================
# Error Codes
# ==========================================================

class ErrorCode(str, Enum):
    """Standardized error codes."""

    INVALID_REQUEST = "INVALID_REQUEST"
    INVALID_INTENT = "INVALID_INTENT"
    UNSUPPORTED_WORKFLOW = "UNSUPPORTED_WORKFLOW"

    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    INVALID_FILE = "INVALID_FILE"

    CONTENT_PROCESSING_ERROR = "CONTENT_PROCESSING_ERROR"
    EDUCATIONAL_AGENT_ERROR = "EDUCATIONAL_AGENT_ERROR"
    MULTIMEDIA_AGENT_ERROR = "MULTIMEDIA_AGENT_ERROR"

    TIMEOUT = "TIMEOUT"
    INTERNAL_ERROR = "INTERNAL_ERROR"


# ==========================================================
# Supported File Types
# ==========================================================

SUPPORTED_FILE_TYPES = (
    ".pdf",
    ".docx",
    ".pptx",
    ".txt",
    ".png",
    ".jpg",
    ".jpeg",
)


# ==========================================================
# Default Messages
# ==========================================================

DEFAULT_SUCCESS_MESSAGE = "Request processed successfully."

DEFAULT_FAILURE_MESSAGE = "Unable to process the request."


# ==========================================================
# Version
# ==========================================================

ORCHESTRATOR_VERSION = "1.0.0"