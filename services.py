import asyncio
from typing import List, Dict, Any, Optional
from github import Github
from atlassian import Jira
from slack_sdk.web.async_client import AsyncWebClient
from config import settings
from models import *

class GitHubService:
    def __init__(self):
        try:
            if settings.github_token:
                self.client = Github(settings.github_token)
            else:
                self.client = None
        except Exception:
            self.client = None
    
    async def get_repositories(self, username: str) -> List[GitHubRepo]:
        """Get repositories for a user"""
        if not self.client:
            raise Exception("GitHub service not configured. Please set GITHUB_TOKEN environment variable.")
        try:
            user = self.client.get_user(username)
            repos = []
            for repo in user.get_repos(type='all', sort='updated')[:10]:  # Limit to 10 most recent
                repos.append(GitHubRepo(
                    name=repo.name,
                    full_name=repo.full_name,
                    description=repo.description,
                    url=repo.html_url,
                    stars=repo.stargazers_count,
                    forks=repo.forks_count
                ))
            return repos
        except Exception as e:
            raise Exception(f"GitHub API error: {str(e)}")
    
    async def get_issues(self, repo_name: str) -> List[GitHubIssue]:
        """Get issues for a repository"""
        if not self.client:
            raise Exception("GitHub service not configured. Please set GITHUB_TOKEN environment variable.")
        try:
            repo = self.client.get_repo(repo_name)
            issues = []
            for issue in repo.get_issues(state='open')[:10]:  # Limit to 10 recent issues
                labels = [label.name for label in issue.labels]
                assignee = issue.assignee.login if issue.assignee else None
                issues.append(GitHubIssue(
                    number=issue.number,
                    title=issue.title,
                    body=issue.body,
                    state=issue.state,
                    assignee=assignee,
                    labels=labels
                ))
            return issues
        except Exception as e:
            raise Exception(f"GitHub API error: {str(e)}")

class JiraService:
    def __init__(self):
        try:
            if settings.jira_url and settings.jira_username and settings.jira_api_token:
                self.client = Jira(
                    url=settings.jira_url,
                    username=settings.jira_username,
                    password=settings.jira_api_token,
                    cloud=True
                )
            else:
                self.client = None
        except Exception:
            self.client = None
    
    async def get_issues(self, project_key: str = None) -> List[JiraIssue]:
        """Get Jira issues"""
        if not self.client:
            raise Exception("Jira service not configured. Please set JIRA_URL, JIRA_USERNAME, and JIRA_API_TOKEN environment variables.")
        try:
            jql = f"project = {project_key}" if project_key else "assignee = currentUser()"
            issues = self.client.jql(jql + " ORDER BY updated DESC", limit=10)
            
            jira_issues = []
            for issue in issues['issues']:
                fields = issue['fields']
                jira_issues.append(JiraIssue(
                    key=issue['key'],
                    summary=fields['summary'],
                    description=fields.get('description', ''),
                    status=fields['status']['name'],
                    assignee=fields['assignee']['displayName'] if fields.get('assignee') else None,
                    priority=fields['priority']['name'] if fields.get('priority') else 'None',
                    issue_type=fields['issuetype']['name']
                ))
            return jira_issues
        except Exception as e:
            raise Exception(f"Jira API error: {str(e)}")
    
    async def create_issue(self, issue_data: CreateJiraIssue) -> str:
        """Create a new Jira issue"""
        if not self.client:
            raise Exception("Jira service not configured. Please set JIRA_URL, JIRA_USERNAME, and JIRA_API_TOKEN environment variables.")
        try:
            issue_dict = {
                'project': {'key': issue_data.project_key},
                'summary': issue_data.summary,
                'description': issue_data.description,
                'issuetype': {'name': issue_data.issue_type},
                'priority': {'name': issue_data.priority}
            }
            
            new_issue = self.client.create_issue(fields=issue_dict)
            return new_issue['key']
        except Exception as e:
            raise Exception(f"Jira API error: {str(e)}")

class SlackService:
    def __init__(self):
        try:
            if settings.slack_bot_token:
                self.client = AsyncWebClient(token=settings.slack_bot_token)
            else:
                self.client = None
        except Exception:
            self.client = None
    
    async def get_channels(self) -> List[SlackChannel]:
        """Get Slack channels"""
        if not self.client:
            raise Exception("Slack service not configured. Please set SLACK_BOT_TOKEN environment variable.")
        try:
            response = await self.client.conversations_list(limit=20)
            channels = []
            
            for channel in response['channels']:
                channels.append(SlackChannel(
                    id=channel['id'],
                    name=channel['name'],
                    is_channel=channel['is_channel'],
                    is_private=channel['is_private'],
                    num_members=channel.get('num_members')
                ))
            return channels
        except Exception as e:
            raise Exception(f"Slack API error: {str(e)}")
    
    async def send_message(self, message_data: SlackMessage) -> str:
        """Send a message to Slack"""
        if not self.client:
            raise Exception("Slack service not configured. Please set SLACK_BOT_TOKEN environment variable.")
        try:
            response = await self.client.chat_postMessage(
                channel=message_data.channel,
                text=message_data.text,
                thread_ts=message_data.thread_ts
            )
            return response['ts']
        except Exception as e:
            raise Exception(f"Slack API error: {str(e)}")
    
    async def get_messages(self, channel: str, limit: int = 10) -> List[Dict]:
        """Get messages from a Slack channel"""
        if not self.client:
            raise Exception("Slack service not configured. Please set SLACK_BOT_TOKEN environment variable.")
        try:
            response = await self.client.conversations_history(
                channel=channel,
                limit=limit
            )
            return response['messages']
        except Exception as e:
            raise Exception(f"Slack API error: {str(e)}")