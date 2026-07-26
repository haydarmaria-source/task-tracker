"""Pydantic models for the Task Tracker.

Baseline (Modules 1-3): title, description, status, priority, assignee.
Mid-course project: due_date (+ computed overdue) and tags.
"""
import re
from datetime import date
from enum import Enum

from pydantic import BaseModel, field_validator

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MAX_TAGS = 10
MAX_TAG_LENGTH = 30


class Status(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


def _clean_str(v: str) -> str:
    return v.strip() if isinstance(v, str) else v


def _validate_due_date(v: str | None) -> str | None:
    """AI assumption corrected: the AI's first draft accepted any string
    that ``datetime.fromisoformat`` could parse (including full
    datetimes like ``2026-07-26T10:00:00``). We only want a plain
    calendar date, so we require the strict ``YYYY-MM-DD`` shape first.
    """
    if v is None:
        return v
    v = _clean_str(v)
    if not v:
        return None
    if not DATE_RE.match(v):
        raise ValueError("due_date must be in YYYY-MM-DD format")
    try:
        date.fromisoformat(v)
    except ValueError:
        raise ValueError("due_date must be a valid calendar date")
    return v


def _validate_tags(v: list[str] | None) -> list[str]:
    if v is None:
        return []
    cleaned: list[str] = []
    for tag in v:
        if not isinstance(tag, str):
            raise ValueError("tags must be strings")
        t = tag.strip()
        if not t:
            raise ValueError("tags must not contain blank values")
        if len(t) > MAX_TAG_LENGTH:
            raise ValueError(f"tags must be {MAX_TAG_LENGTH} characters or fewer")
        cleaned.append(t)
    if len(cleaned) > MAX_TAGS:
        raise ValueError(f"a task may have at most {MAX_TAGS} tags")
    return cleaned


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    status: Status = Status.todo
    priority: Priority = Priority.medium
    assignee: str = ""
    due_date: str | None = None
    tags: list[str] = []

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        v = _clean_str(v)
        if not v:
            raise ValueError("title must not be blank")
        return v

    @field_validator("due_date")
    @classmethod
    def due_date_valid(cls, v):
        return _validate_due_date(v)

    @field_validator("tags")
    @classmethod
    def tags_valid(cls, v):
        return _validate_tags(v)


class TaskUpdate(BaseModel):
    """Partial update. Every field is optional; only provided fields change."""

    title: str | None = None
    description: str | None = None
    status: Status | None = None
    priority: Priority | None = None
    assignee: str | None = None
    due_date: str | None = None
    tags: list[str] | None = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v):
        if v is None:
            return v
        v = _clean_str(v)
        if not v:
            raise ValueError("title must not be blank")
        return v

    @field_validator("due_date")
    @classmethod
    def due_date_valid(cls, v):
        return _validate_due_date(v)

    @field_validator("tags")
    @classmethod
    def tags_valid(cls, v):
        if v is None:
            return None
        return _validate_tags(v)


class Task(BaseModel):
    id: int
    title: str
    description: str
    status: Status
    priority: Priority
    assignee: str
    due_date: str | None = None
    tags: list[str] = []
    overdue: bool = False
    created_at: str
    updated_at: str
