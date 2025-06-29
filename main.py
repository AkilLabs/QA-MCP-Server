from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
import asyncio

from config import settings
from models import *
from services import GitHubService, JiraService, SlackService

app = FastAPI(
    title="Multi-Service MCP Server",
    description="MCP Server with GitHub, Jira, Salesforce, and Slack integrations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
github_service = GitHubService()
jira_service = JiraService()
slack_service = SlackService()

@app.get("/")
async def root():
    return {
        "message": "Multi-Service MCP Server",
        "version": "1.0.0",
        "services": ["GitHub", "Jira", "Slack"]
    }

# GitHub Endpoints
@app.get("/github/repos/{username}", response_model=List[GitHubRepo])
async def get_github_repos(username: str):
    """Get GitHub repositories for a user"""
    try:
        return await github_service.get_repositories(username)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/github/issues/{repo_name:path}", response_model=List[GitHubIssue])
async def get_github_issues(repo_name: str):
    """Get GitHub issues for a repository"""
    try:
        return await github_service.get_issues(repo_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Jira Endpoints
@app.get("/jira/issues", response_model=List[JiraIssue])
async def get_jira_issues(project_key: Optional[str] = None):
    """Get Jira issues"""
    try:
        return await jira_service.get_issues(project_key)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/jira/issues")
async def create_jira_issue(issue_data: CreateJiraIssue):
    """Create a new Jira issue"""
    try:
        issue_key = await jira_service.create_issue(issue_data)
        return {"success": True, "issue_key": issue_key}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Slack Endpoints
@app.get("/slack/channels", response_model=List[SlackChannel])
async def get_slack_channels():
    """Get Slack channels"""
    try:
        return await slack_service.get_channels()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/slack/messages")
async def send_slack_message(message_data: SlackMessage):
    """Send a message to Slack"""
    try:
        message_ts = await slack_service.send_message(message_data)
        return {"success": True, "message_ts": message_ts}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/slack/messages/{channel}")
async def get_slack_messages(channel: str, limit: int = 10):
    """Get messages from a Slack channel"""
    try:
        messages = await slack_service.get_messages(channel, limit)
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# MCP Protocol Endpoints
@app.post("/mcp/call")
async def mcp_call(request: MCPRequest):
    """Generic MCP call handler"""
    try:
        method = request.method
        params = request.params
        
        # Route MCP calls to appropriate services
        if method.startswith("github."):
            if method == "github.get_repos":
                data = await github_service.get_repositories(params.get("username"))
            elif method == "github.get_issues":
                data = await github_service.get_issues(params.get("repo_name"))
            else:
                raise ValueError(f"Unknown GitHub method: {method}")
                
        elif method.startswith("jira."):
            if method == "jira.get_issues":
                data = await jira_service.get_issues(params.get("project_key"))
            elif method == "jira.create_issue":
                issue_data = CreateJiraIssue(**params)
                data = await jira_service.create_issue(issue_data)
            else:
                raise ValueError(f"Unknown Jira method: {method}")
                
        elif method.startswith("slack."):
            if method == "slack.get_channels":
                data = await slack_service.get_channels()
            elif method == "slack.send_message":
                message_data = SlackMessage(**params)
                data = await slack_service.send_message(message_data)
            elif method == "slack.get_messages":
                data = await slack_service.get_messages(params.get("channel"), params.get("limit", 10))
            else:
                raise ValueError(f"Unknown Slack method: {method}")
        else:
            raise ValueError(f"Unknown service method: {method}")
            
        return MCPResponse(success=True, data=data)
        
    except Exception as e:
        return MCPResponse(success=False, error=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2025-06-29"}

# Connection test endpoints
@app.get("/test-connections")
async def test_all_connections():
    """Test connections to all configured services"""
    results = {}
    
    # Test GitHub connection
    try:
        if github_service.client:
            # Try to get the authenticated user
            user = github_service.client.get_user()
            results["github"] = {
                "status": "connected",
                "user": user.login,
                "name": user.name
            }
        else:
            results["github"] = {"status": "not_configured", "message": "GITHUB_TOKEN not set"}
    except Exception as e:
        results["github"] = {"status": "error", "message": str(e)}
    
    # Test Jira connection
    try:
        if jira_service.client:
            # Try to get server info
            server_info = jira_service.client.server_info()
            results["jira"] = {
                "status": "connected",
                "server_title": server_info.get("serverTitle", "Unknown"),
                "version": server_info.get("version", "Unknown")
            }
        else:
            results["jira"] = {"status": "not_configured", "message": "Jira credentials not set"}
    except Exception as e:
        results["jira"] = {"status": "error", "message": str(e)}
    
    # Test Slack connection
    try:
        if slack_service.client:
            # Try to get auth test
            response = await slack_service.client.auth_test()
            results["slack"] = {
                "status": "connected",
                "user": response.get("user", "Unknown"),
                "team": response.get("team", "Unknown")
            }
        else:
            results["slack"] = {"status": "not_configured", "message": "SLACK_BOT_TOKEN not set"}
    except Exception as e:
        results["slack"] = {"status": "error", "message": str(e)}
    
    return {"connection_tests": results}

@app.get("/test-github")
async def test_github_connection():
    """Test GitHub connection specifically"""
    try:
        if not github_service.client:
            return {"status": "not_configured", "message": "GITHUB_TOKEN not set"}
        
        user = github_service.client.get_user()
        return {
            "status": "connected",
            "user": user.login,
            "name": user.name,
            "public_repos": user.public_repos,
            "private_repos": user.total_private_repos
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/test-jira")
async def test_jira_connection():
    """Test Jira connection specifically"""
    try:
        if not jira_service.client:
            return {"status": "not_configured", "message": "Jira credentials not set"}
        
        server_info = jira_service.client.server_info()
        return {
            "status": "connected",
            "server_title": server_info.get("serverTitle", "Unknown"),
            "version": server_info.get("version", "Unknown"),
            "base_url": server_info.get("baseUrl", "Unknown")
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/test-slack")
async def test_slack_connection():
    """Test Slack connection specifically"""
    try:
        if not slack_service.client:
            return {"status": "not_configured", "message": "SLACK_BOT_TOKEN not set"}
        
        response = await slack_service.client.auth_test()
        return {
            "status": "connected",
            "user": response.get("user", "Unknown"),
            "user_id": response.get("user_id", "Unknown"),
            "team": response.get("team", "Unknown"),
            "team_id": response.get("team_id", "Unknown")
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )