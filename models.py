from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class MCPRequest(BaseModel):
    method: str
    params: Dict[str, Any]

class MCPResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

# GitHub Models
class GitHubRepo(BaseModel):
    name: str
    full_name: str
    description: Optional[str]
    url: str
    stars: int
    forks: int

class GitHubIssue(BaseModel):
    number: int
    title: str
    body: Optional[str]
    state: str
    assignee: Optional[str]
    labels: List[str]

# Jira Models
class JiraIssue(BaseModel):
    key: str
    summary: str
    description: Optional[str]
    status: str
    assignee: Optional[str]
    priority: str
    issue_type: str

class CreateJiraIssue(BaseModel):
    project_key: str
    summary: str
    description: str
    issue_type: str = "Task"
    priority: str = "Medium"

# Slack Models
class SlackMessage(BaseModel):
    channel: str
    text: str
    thread_ts: Optional[str] = None

class SlackChannel(BaseModel):
    id: str
    name: str
    is_channel: bool
    is_private: bool
    num_members: Optional[int]