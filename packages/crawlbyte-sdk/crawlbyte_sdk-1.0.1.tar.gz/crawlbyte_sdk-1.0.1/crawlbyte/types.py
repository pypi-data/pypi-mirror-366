from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class Task:
    id: str
    type: str
    status: str
    url: Optional[str] = None
    input: Optional[List[str]] = None
    fields: Optional[List[str]] = None
    method: Optional[str] = None
    body: Optional[str] = None
    proxy: Optional[str] = None
    customHeaders: Optional[Dict[str, str]] = None
    customHeaderOrder: Optional[List[str]] = None
    jsRendering: Optional[bool] = None
    customSelector: Optional[str] = None
    userAgentPreset: Optional[str] = None
    userAgentCustom: Optional[str] = None
    dataType: Optional[str] = None
    location: Optional[str] = None
    sortBy: Optional[str] = None
    result: Optional[Any] = None
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    createdAt: str = ""
    updatedAt: Optional[str] = None

@dataclass
class TaskPayload:
    type: str
    url: Optional[str] = None
    location: Optional[str] = None
    sortBy: Optional[str] = None
    dataType: Optional[str] = None
    method: Optional[str] = None
    jsRendering: Optional[bool] = None
    customSelector: Optional[str] = None
    userAgentPreset: Optional[str] = None
    userAgentCustom: Optional[str] = None
    proxy: Optional[str] = None
    customHeaderOrder: Optional[List[str]] = None
    input: Optional[List[str]] = None
    customHeaders: Optional[Dict[str, str]] = None
    fields: Optional[List[str]] = None
    body: Optional[str] = None
    multithread: Optional[bool] = None

@dataclass
class PollOptions:
    interval_seconds: int
    timeout_seconds: int
